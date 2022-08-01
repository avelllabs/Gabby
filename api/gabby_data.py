

from soupsieve import match
from sqlalchemy import create_engine
import psycopg2 
import io
import pandas as pd
import numpy as np
from collections import Counter

conn_string = 'postgresql+psycopg2://gabbydbuser:gabbyDBpass@localhost:5432/gabbyDB'
db = create_engine(conn_string)
conn = db.connect()


def filter_phrases_containing_brand_model_terms(df, brand_model_terms):
    pattern = '(' + '|'.join(brand_model_terms) + ')'
    return df[ ~df['phrase'].str.match(pattern, case=False)]

def is_alpha_numeric(df):
    """
    checking if every token in the phrase is not a string of punctuations
    """
    alnums =  df['phrase'].apply(lambda p: all([t.isalnum() for t in p.split()]))
    return df[alnums]

def drop_numeric_phrases(df):
    """
    remove phrases that are just numbers
    """
    return df[~df['phrase'].apply(lambda p: len(p.split()) == 1 and p.isnumeric())]


def get_attributes_list():
    negative_attributes_query = \
    '''SELECT  P.key_phrase_id, P.phrase, S.n_positive, S.n_negative, S.reviewer_idf, S.n_reviews, S.n_reviewers
    FROM key_phrase_root P, 
    (SELECT * 
    FROM key_phrase_scores 
    WHERE  n_positive - n_negative < 0 
    ORDER BY n_negative DESC LIMIT 50) S
    WHERE P.key_phrase_id=S.key_phrase_id 
    ORDER BY n_reviewers DESC
    '''
    negative_phrases = pd.read_sql(negative_attributes_query, conn)

    positive_attributes_query = \
     '''SELECT  P.key_phrase_id, P.phrase, S.n_positive, S.n_negative, S.reviewer_idf, S.n_reviews, S.n_reviewers
    FROM key_phrase_root P, 
    (SELECT * 
    FROM key_phrase_scores 
    WHERE  n_positive - n_negative > 0 
    ORDER BY n_positive DESC LIMIT 50) S
    WHERE P.key_phrase_id=S.key_phrase_id 
    ORDER BY n_positive DESC
    '''
    positive_phrases = pd.read_sql(positive_attributes_query, conn)

    monitor_brands_query = \
    '''SELECT DISTINCT(brand)
        FROM baseline_products 
        WHERE title ILIKE '%%inch%%' 
        AND title ILIKE '%%monitor%%' 
    '''
    monitor_brands = pd.read_sql(monitor_brands_query, conn)

    attributes = pd.concat([positive_phrases, negative_phrases]).reset_index(drop=True)

    attributes_filtered = \
        filter_phrases_containing_brand_model_terms(
                drop_numeric_phrases(
                        is_alpha_numeric(attributes)
                ), 
                monitor_brands[monitor_brands['brand'].str.len() > 1]['brand'].tolist()
        )
    
    return attributes_filtered[['key_phrase_id', 'phrase']].sample(50)


def get_reviews_for_attributes(query_attributes):
    phrase_ids_query = \
    f'''SELECT key_phrase_id, phrase 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(query_attributes)}')
    '''
    query_phrases = pd.read_sql(phrase_ids_query, conn)

    review_results_query = \
    '''SELECT key_phrase_id, review_id 
        FROM key_phrase_reviews 
        WHERE key_phrase_id IN 
        (SELECT key_phrase_id 
        FROM key_phrase_root 
        WHERE phrase IN ('the price', 'the stand', '2 weeks', 'quality'))
    '''
    review_ids_for_query = pd.read_sql(review_results_query, conn)
    review_ids_for_query = review_ids_for_query.merge(query_phrases, on='key_phrase_id', how='left')
    review_ids_for_query = review_ids_for_query.groupby('review_id')['phrase'].apply(list).reset_index()
    review_ids_for_query['n_matches'] = review_ids_for_query['phrase'].apply(len)
    top_matched_reviews = review_ids_for_query.sort_values('n_matches', ascending=False).head(25)

    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
            {','.join(top_matched_reviews['review_id'].astype(str).tolist())}
        )
        
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(top_matched_reviews, on='review_id')
    return matched_reviews



def get_products_for_attributes_and_liked_reviews(attributes, liked_reviews = []):
    # TODO: ignoring the liked reviews for now

    phrase_ids_query = \
    f'''SELECT key_phrase_id, phrase 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(attributes)}')
    '''
    query_phrases = pd.read_sql(phrase_ids_query, conn)

    review_results_query = \
    '''SELECT key_phrase_id, review_id 
        FROM key_phrase_reviews 
        WHERE key_phrase_id IN 
        (SELECT key_phrase_id 
        FROM key_phrase_root 
        WHERE phrase IN ('the price', 'the stand', '2 weeks', 'quality'))
    '''
    review_ids_for_query = pd.read_sql(review_results_query, conn)
    review_ids_for_query = review_ids_for_query.merge(query_phrases, on='key_phrase_id', how='left')
    review_ids_for_query = review_ids_for_query.groupby('review_id')['phrase'].apply(list).reset_index()
    review_ids_for_query['n_matches'] = review_ids_for_query['phrase'].apply(len)

    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
            {','.join(review_ids_for_query['review_id'].astype(str).tolist())}
        )
        
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(review_ids_for_query, on='review_id')

    product_ranking = matched_reviews.groupby(['asin']).agg({
        'n_matches': 'sum',
        'rating': 'mean',
        'verified': 'sum',
        'vote': 'sum',
        'review_id': 'count',
        'phrase': 'sum'
    }).sort_values(['n_matches', 'verified', 'rating', 'review_id', 'vote'], ascending=False).reset_index()
    product_ranking['phrase'] = product_ranking['phrase'].apply(lambda x: Counter(x))
    product_ranking = product_ranking.rename(columns={'review_id': 'n_reviews'})
    return product_ranking.head(10)




sample_response_attributes = [{"key_phrase_id":8968,"phrase":"30 days"},{"key_phrase_id":21,"phrase":"the speakers"},{"key_phrase_id":372,"phrase":"the base"},{"key_phrase_id":7152,"phrase":"a company"},{"key_phrase_id":819,"phrase":"monitor"},{"key_phrase_id":200,"phrase":"the brightness"},{"key_phrase_id":4953,"phrase":"the issues"},{"key_phrase_id":4223,"phrase":"the resolution"},{"key_phrase_id":4864,"phrase":"monitors"},{"key_phrase_id":9,"phrase":"the screen"},{"key_phrase_id":57,"phrase":"a monitor"},{"key_phrase_id":2444,"phrase":"great monitor"},{"key_phrase_id":3559,"phrase":"3 months"},{"key_phrase_id":12190,"phrase":"no avail"},{"key_phrase_id":109,"phrase":"gaming"},{"key_phrase_id":90,"phrase":"customer service"},{"key_phrase_id":2351,"phrase":"hdmi"},{"key_phrase_id":39,"phrase":"time"},{"key_phrase_id":7184,"phrase":"no way"},{"key_phrase_id":7338,"phrase":"2 weeks"},{"key_phrase_id":11869,"phrase":"no help"},{"key_phrase_id":18154,"phrase":"a dead pixel"},{"key_phrase_id":41,"phrase":"amazon"},{"key_phrase_id":18621,"phrase":"4k"},{"key_phrase_id":76,"phrase":"brightness"},{"key_phrase_id":8745,"phrase":"crap"},{"key_phrase_id":3,"phrase":"this monitor"},{"key_phrase_id":763,"phrase":"tech support"},{"key_phrase_id":880,"phrase":"speakers"},{"key_phrase_id":37,"phrase":"the quality"},{"key_phrase_id":4101,"phrase":"your time"},{"key_phrase_id":17270,"phrase":"144hz"},{"key_phrase_id":2122,"phrase":"games"},{"key_phrase_id":494,"phrase":"quality"},{"key_phrase_id":2383,"phrase":"the colors"},{"key_phrase_id":3258,"phrase":"this issue"},{"key_phrase_id":1029,"phrase":"this product"},{"key_phrase_id":2007,"phrase":"the box"},{"key_phrase_id":2841,"phrase":"junk"},{"key_phrase_id":450,"phrase":"replacement"},{"key_phrase_id":3660,"phrase":"work"},{"key_phrase_id":5524,"phrase":"garbage"},{"key_phrase_id":1697,"phrase":"your money"},{"key_phrase_id":12691,"phrase":"an hour"},{"key_phrase_id":2323,"phrase":"this problem"},{"key_phrase_id":735,"phrase":"return"},{"key_phrase_id":5506,"phrase":"two stars"},{"key_phrase_id":32248,"phrase":"these issues"},{"key_phrase_id":8067,"phrase":"arrival"},{"key_phrase_id":597,"phrase":"a lot"}]

sample_response_reviews = [{"review_id":112406,"rating":5.0,"sentiment":"positive","vote":0.0,"verified":True,"reviewerID":"A28GZ52326W7ET","asin":"B00139S3U6","reviewText":"The latest generation of Hewlett Packard widescreen computer monitors sets a new standard for quality and value, and this model is probably just about right for your average desktop user. At 22inches, it takes up a fair amount of space on your desktop, but it is not overwhelming, and at under $300, the price is close to the generic competition. I spent quite a bit of time researching and comparing LCD monitors, and HP clearly is a cut above for roughly the same money. This monitor is more attractive visually, and its adjustability up and down, and 90 degree rotation option may be of importance to many consumers. I opened the box, hooked it up, installed the software, and haven't touched anything since. This model and similar HP monitors are some of the best deals out there for a desktop user who believes that it is worth paying a few dollars more for a clearly superior product.\n\n<a data-hook=\"product-link-linked\" class=\"a-link-normal\" href=\"\/HP-W2207H-22-inch-Widescreen-LCD-Monitor\/dp\/B00139S3U6\/ref=cm_cr_arp_d_rvw_txt?ie=UTF8\">HP W2207H 22-inch Widescreen LCD Monitor<\/a>","reviewTitle":"HP Monitor Beats The Competition","reviewTime":1229731200000,"phrase":[None,None],"n_matches":2},{"review_id":173319,"rating":3.0,"sentiment":"negative","vote":5.0,"verified":True,"reviewerID":"A1WT047CVF256C","asin":"B001LYPNFQ","reviewText":"Overall a nice monitor. Yes, it has tint problems out of the box, but you should calibrate every monitor you get anyway, regardless of quality. It can make a huge difference, even if you're not editing photos or the like. Calibration solves the monitor's blue tint problem completely, so it would seem to simply be a matter of poorly selected defaults at the factory.\n\nI only have two complaints. The first is a simple problem that Asus simply should not have overlooked. The monitor has no height adjustment, and the stand is pretty short. If you set it on a desk with proper height adjustment for your arms, the screen will likely be too low for you. I put mine on a nice solid mounting arm to solve the problem. The second is more serious, and concerns the picture quality. I am driving my monitor from a brand new Mac Mini through the HDMI port, and there seem to be color bleed issues. The edge of bright colors should be sharp and crisp, but the left and right edges bleed over noticeably, at a darker color level, yielding what looks like a sort of faint line on the edge. I have the screen in native 1920x1200 mode, so there really shouldn't be any antialiasing issues or somesuch. In any case, none of the other monitors I've used with the mac (3 others today) have this problem. This seems to happen more with certain colors than others, and does appear to depend on the background to some extent. Bright reds and greens are the worst, bleeding over a couple of pixels, but other darker colors don't seem as bad. This could be due to the fact that I'm using HDMI instead of DVI, but since I run dual-headed (and my other permanent monitor doesn't have HDMI), I have little choice.\n\nBecause of the color bleed issue, I would not recommend this monitor for things like photo\/video editing, or anything that requires clean, sharp lines. But as a monitor for everyday browsing, document editing, and probably games (this is for work, so I won't be trying out any games on it), it should be fine. The price is right, at least.","reviewTitle":"I would give 3.5 stars if it were possible","reviewTime":1288656000000,"phrase":[None,None,None],"n_matches":3},{"review_id":209586,"rating":5.0,"sentiment":"positive","vote":12.0,"verified":False,"reviewerID":"A25A7C826KIX2R","asin":"B002MT6SDU","reviewText":"I bought this to replace an older 4:3 Princeton LCD.  Worked fine right out of the box with my Lenovo T61 laptop and its built in NVidia graphics card.  My previous experience with 15-17\" widescreens was poor because they had a much smaller effective screen height than 4:3 which resulted in very small text and graphics for a given screen size.  For example, my 15.4' laptop widescreen is very difficult to view with the native resolution of 1920x1080.  The 25\" diagonal width worked out to be about the same height as my 4:3 LCD which is what I wanted: I didn't want to lose any screen height.  I was concerned that the resolution might be too small to read but it worked out about the same.  My 19\" LCD 4:3 displayed 1280x1024 and this HP displays 1920x1080 so the text and icons are about the same size.  I use this for business purposes so the widescreen format wasn't important but having the extra screen width with the same height as the monitor I was replacing was important for viewing multiple windows side by side.  I wound up buying a Planar dual display mount and have the older monitor and the HP side by side in dual display mode.  The Lenovo T61 NVidea card is capable of dual monitor displays.  I have PLENTY of workspace now and although it looks a little odd with a 4:3 next to the widescreen, it works well for me.\n\nThis HP monitor has VGA, DVI and HDMI ports and it comes with one of each cable in the box.  The stand is a little flimsy and the monitor will wiggle if bumped.  As I stated above, I took the stand off and use the Planar dual mount which is very rigid.  As for the screen, the monitor has excellent contrast and color.  Yes - The screen is a little shiny and has a little reflection but it is no worse than CRT's and I think this shiny front gives the monitor the rich colors and excellent contrast. I use this in a very bright office with lots of sun and have no problems.  You might have some issues if light is behind you though.\n\nCan't go wrong with this one.  I noticed the price has gone up.  I paid $279 for mine before Xmas and now it is up to $297 but still worth it for this size, quality and name brand.","reviewTitle":"Excellent Monitor","reviewTime":1262044800000,"phrase":[None,None,None],"n_matches":3},{"review_id":227216,"rating":5.0,"sentiment":"positive","vote":0.0,"verified":True,"reviewerID":"A3NM39O6R8H3A5","asin":"B0039648BO","reviewText":"I'm going to start this review of with what I feel are this monitors shortcomings, because there really aren't that many of them.\nAlso keep in mind that, my opinion of a pro or con, feature wise, may be reversed for someone else. It's all based on personal preference really. I'll attempt to be as objective as possible.\nCONS\nFirst and foremost..\nI. Price. quality doesn't come cheap and the Dell U2711 is no exception. I have been considering a Dell U3011 for sometime now, but the price always turned me away, and the U2711 wasn't significantly cheaper. However I just happened to come across this monitor again the other day for $650. My response? Shut up and take my money. The cheapest I've ever seen a brand new one was about $900. I hope these continue to get cheaper because I would like to buy at least two more in the future.\nII. Size. 27 inches is bigger than the average desktop monitor, but the U2711 is a monster and it's heavy too. The FED EX driver was quick to comment on that. I don't really consider this much of a con though. I like my computer hardware to be sturdy and well built. If you plan to mount this beast you will want to buy a very good mount.\nIII. ghosting and response time. My last monitor was a 27 inch samsung syncmaster. I'm not really noticing much of a difference in the response times. 1ms response time vs 6ms is almost None. I do believe there is a bit of ghosting in gaming. This may be a deal breaker for FPS players. I will need more time to play different games to really test this. So far I have only played Skyrim and it seems perfectly fine.\nIV. Anti-glare. The anti-glare coating is only noticeable on whites for the most part. It doesn't bother me. I actually kind of like it.\nPROS\nI. Resolution. The main reason I bought this monitor. I wanted to game at 1440p. It's even better than I thought it would be. You will never want to go back to 1080p.\nII. Color. This wasn't really something I thought I would care that much about. My Samsung monitor had great color, but this thing blows it out of the water. going from 16.7 million to 1.07 BILLION is night and day. I can see why a photographer would love this monitor.\nIII. Inputs. I've never seen so many inputs on a monitor. I especially like the USB and SD card slots. Though someone should probably tell Dell that VGA cables are no longer the standard. Out of the box, a VGA cable was plugged into the back. Maybe they're just trying to get rid of them? I digress. I was happy to see that it did come with cables, even a display port cable was included. A premium monitor should come with all the accessories. thank you Dell.\nIV. Controls. Best controls ever. Seriously, every monitor I've owned has had terrible controls. Switching between different presets and changing brightness is very easy.\nV. Housing and Stand. This is a professional monitor and it definitely shows. It's not glossy or gimmicky. There were no annoying stickers all over the monitor. I love the stand on this monitor. It doesn't feel like it may break in 6 months. It's built to last. It also slides up and down, which is my favorite feature, and left and right. Overall the housing is very plain. The minimalist will love this. I know I do.\nVI. Packaging. The U2711 came in very good packaging. I was impressed.\n\nFinal thoughts\nThere's very little reason not to buy this monitor. In the future I may regret not going with the U3011, but the price was so much lower on the U2711 at the time so the choice was obvious. If it comes down to it and the price difference becomes less than about $200, then go with the U3011. One other reason not to buy this monitor would be whether your system can handle the resolution. Skyrim runs at about 30-40FPS on my system. Though it may run higher if I didn't have 20 or so graphics mods installed.\nHere are my specs so you can have some sort of idea what you will need.\n\nCPU: Intel Core I5 2500k @ 4Ghz\nRAM: 16gb Corsair Vengeance 1600Mhz\nMotherboard: Gigabyte Z68\nVideo Card: MSI Radeon 7950 with arctic accellero 7970 cooler\nSSD: Samsung 840 pro 256GB\nHDD: Standard issue 1TB\nPSU thermaltake 850 watt modular.\n\nYou can probably get by on lesser specs, but you will take a performance hit. 2560x1440=3,686,400 total pixels, 1920x1080=2,073,600. That's almost %60 more pixels your computer will have to process. 1080p pushes a lot of PC's to their limits as it is.\n\nI recommend buying new as well. Supposedly some of the earlier models had problems.\nI hope this has been informative\nCheers!","reviewTitle":"Best purchase I have made this year","reviewTime":1354060800000,"phrase":[None,None,None],"n_matches":3},{"review_id":222049,"rating":5.0,"sentiment":"positive","vote":0.0,"verified":True,"reviewerID":"A3376ZXV304DQV","asin":"B002ZVCGXQ","reviewText":"This has to be the best monitor you can buy for the price.\n\nPros:\nPrice - for under two hundred, a bargain.\nQuality - the best monitor I've ever owned. No dead pixels, scratches, or anything. When you pick it up you can tell it is well built all around. The design looks so amazing people will think you own a $500 monitor. Also the monitor produces no heat.\nWeight - can easily lift and probably the lightest monitor you can own for a comparable size.\nScreen - full HD quality 1920x1080. I have it plugged in to a ATI HD5850 and games and movies play great.\nTouch buttons - great response time and look nice.\n\nCons: (The cons below don't even come close to knocking off a star from this rating of 5 stars. I just listed as an FYI)\nStand - the monitor always has a tilt because of the stand design. The quickest and most effective way I found to fix this was put something under the stand which solves that problem.\nAC\/DC coveter - way hotter than it should be. The monitor would hardly use any power if they had designed the adapter better and didn't create so much heat.","reviewTitle":"Great Product","reviewTime":1279843200000,"phrase":[None,None,None],"n_matches":3}]


sample_response_products = [{"asin":"B0098Y77U0","n_matches":339,"rating":4.2736156352,"verified":288,"vote":322.0,"n_reviews":307,"phrase":{"the price":232,"the stand":82,"quality":25}},{"asin":"B015WCV70W","n_matches":226,"rating":4.5399061033,"verified":199,"vote":675.0,"n_reviews":213,"phrase":{"the price":162,"the stand":46,"quality":16,"2 weeks":2}},{"asin":"B003Y3BJ7S","n_matches":159,"rating":4.5442176871,"verified":139,"vote":1188.0,"n_reviews":147,"phrase":{"the stand":21,"the price":120,"quality":18}},{"asin":"B00EZSUWFG","n_matches":131,"rating":4.3360655738,"verified":114,"vote":463.0,"n_reviews":122,"phrase":{"the price":93,"the stand":25,"quality":13}},{"asin":"B00C8T5KOW","n_matches":123,"rating":4.3304347826,"verified":106,"vote":143.0,"n_reviews":115,"phrase":{"the price":95,"quality":12,"the stand":16}}]