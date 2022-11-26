(ns gabby-rf.views
  (:require
   [gabby-rf.events :as events]
   [gabby-rf.routes :as routes]
   [gabby-rf.subs :as subs]
   [re-com.core :refer [modal-panel at v-box]]
   [re-frame.core :as re-frame]
   [reagent.core :as reagent]
   [clojure.string :as str]))


(def attributes-list
  [{:label "Decent Price"}
   {:label "Color" :active true}
   {:label "Quality build"}
   {:label "Customer service"}
   {:label "Volume"}
   {:label "Brightness" :active true}
   {:label "Easy to use"}
   {:label "Long battery life" :active true}
   {:label "Cleaning"}
   {:label "Good sound quality" :active true}
   {:label "Scent"}
   {:label "Battery life"}
   {:label "Cord length"}
   {:label "Durability" :active true}
   {:label "Camera quality" :active true}
   {:label "Display size" :active true}])

;; TODO remove ids and to classes

(defn common-header [active-panel current-product]
  (let [navigate-to (fn [panel]
                      (case panel
                        :product-attributes-panel :product-index
                        :product-reviews-panel [:product-attributes :produit current-product]
                        :product-index-panel :home))]
    [:div.row.common-header
     [:div.col
      [:button.back-button.float-left.mt-2
       {:on-click #(re-frame/dispatch [::events/navigate (navigate-to active-panel)])}
       [:img {:src "/images/arrow_back.svg"}]]] ;; TODO add logic to hide and show
     [:div.col-auto
      [:a#logo
       {:href "https://joingabby.com"
        :target "_blank"}
       [:img {:src "/images/LOGO.svg"}]]]
     [:div.col
      (when (not (= active-panel :product-index-panel))
        [:button.btn.btn_restart.float-right
         {:on-click #(re-frame/dispatch [::events/navigate :product-index])}
         "Restart"])]])
  )

;; FIX: for Mailerlite form to re-render when navigating back to landing page
;; TODO: more description
(defn fetch-render-ml-form []
  (-> (js/fetch
       "https://assets.mailerlite.com/jsonp/186743/forms/YnqWxP?callback=ml.fn.renderEmbeddedForm"
       #js
       {:headers
        #js
        {:accept "*/*",
         :accept-language "en-US,en;q=0.9",
         :cache-control "no-cache",
         :pragma "no-cache",
         :sec-fetch-dest "script",
         :sec-fetch-mode "no-cors",
         :sec-fetch-site "cross-site"},
        :referrerPolicy "strict-origin-when-cross-origin",
        :body nil,
        :method "GET",
        :mode "cors",
        :credentials "omit"})
      (.then (fn [res]
               (.text res)))
      (.then (fn [res]
               {:ml-fn (last (str/split (str/join (take 24 (subs res 4))) #"\."))
                :fn-param (str/join (drop-last 2 (drop 1 (subs res 28))))}))
      (.then (fn [res]
               ((.ml js/window (:ml-fn res) (.parse js/window.JSON (:fn-param res))))))))


;; home
(defn mailerlite-embedded-form []
  (reagent/create-class
   {:component-did-mount
    (fn []
      (.setTimeout js/window (fn []
                               (let [ml-form (.querySelectorAll js/document ".ml-embedded")]
                                 (when (empty? (aget ml-form 0 "innerHTML")) (fetch-render-ml-form))))))

    ;; ... other methods go here
    ;; see https://facebook.github.io/react/docs/react-component.html#the-component-lifecycle
    ;; for a complete list

    ;; name your component for inclusion in error messages
    :display-name "mailerlite-embedded-form"

    :reagent-render
    (fn []
      [:div {:class "ml-embedded"
             :data-form "YnqWxP"}])}))

(defn home-panel []
  (let [attributes-list attributes-list
        user-email @(re-frame/subscribe [::subs/user-email])
        user-subscribed? @(re-frame/subscribe [::subs/subscribed?])]
    [:div.home-panel
     [:div.top-section
      [:div.container
       [:div.masthead
        [:div
         [:div
          [:div#logo
           [:img {:src "/images/LOGO.svg"}]]]]
        [:div.headline-wrap.align-items-center.justify-content-center
         [:div
          [:div.headline
           "We search for the world's best reviews"]]]
        [:div.subheading-wrap.align-items-center.justify-content-center
         [:div.col.mx-auto
          [:div.subheading
           "Stop wasting time - Gabby helps you find products that matter to you"]]]
        [:div.top-section-ctas
         [:a.btn.btn_launchapp
          {:role "button"
           :on-click #(re-frame/dispatch [::events/navigate :product-index])}
          "GIVE IT A TRY - IT'S FREE"]]]]]

     [:div.middle-section
      [:div.container.middle-section-container
       [:div.row.align-items-center.justify-content-center.middle-section-main-group
        [:div.landing-products-img-desktop.col-md-7.text-center.d-none.d-lg-block.d-sm-none.d-md-none
         [:img {:src "images/landing_products.png"}]]
        [:div.col-sm-8.col-md-8.col-lg-5
         [:div.section_heading
          "Pick your product"]
         [:div.section_text
          "Select a product category that you care about"]
         [:div.row.align-items-center.justify-content-center
          [:div.col-xs-12.col-sm-12
           [:img.d-block.d-xs-block.d-sm-block.d-lg-none.d-none
            {:src "images/landing_products.png"}]]]
         [:a.btn.btn_launchapp
          {:role "button"
           :on-click #(re-frame/dispatch [::events/navigate :product-index])}
          "CHECK OUT GABBY - IT'S FREE"]]]

       [:div.row.align-items-center.justify-content-center.middle-section-sub-group
        [:div.col-12.text-center
         [:div.section_heading
          "Let us know what matters to you"]
         [:div.section_text
          "Pick what you care about, and select reviews that you like, we will do the rest"]]

        [:div.attributes_list
         (for [group (partition 5 attributes-list)]
           ^{:key group}
           [:div.attributes-list-group
            [:div.btn-group-toggle
             (for [item group]
               ^{:key item}
               [:label.btn.attribute_tag
                {:class (when (true? (:active item)) "active")}
                [:input
                 {:type "checkbox"}] (:label item)])]])]

        [:div.row.align-items-center.justify-content-center.middle-section-footer
         [:div.col-md-7.d-none.d-lg-block.d-sm-none.d-md-none
          [:img.img-fluid
           {:src "images/landing_img2.png"}]
          ;; [:lottie-player.img-fluid
          ;;  {:src "https://lottie.host/ef992465-b4cc-4919-9bf7-710a6e0533d3/A2l6EIjIoy.json"
          ;;   :background "transparent"
          ;;   :speed "1"
          ;;   :autoplay ""
          ;;   }]
          ]

         [:div.col-sm-8.col-md-8.col-lg-5.text-left
          [:div.section_heading
           "We'll do the work"]
          [:div.section_text
           "Gabby will show you all the best products based on the features you choose"]
          [:div.row.align-items-center.justify-content-center
           [:div.col-xs-12.col-sm-12
            [:img.d-block.d-xs-block.d-sm-block.d-lg-none.d-none
             {:src "images/landing_img2.png"}]
            ;; [:lottie-player.img-fluid.d-block.d-xs-block.d-sm-block.d-lg-none.d-none
            ;;  {:src "https://lottie.host/ef992465-b4cc-4919-9bf7-710a6e0533d3/A2l6EIjIoy.json"
            ;;   :background "transparent"
            ;;   :speed "1"
            ;;   :autoplay ""}]
            ]]
          [:a.btn.btn_launchapp
           {:role "button"
            :on-click #(re-frame/dispatch [::events/navigate :product-index])}
           "CHECK OUT GABBY - IT'S FREE"]]]]]]
     [:div.bottom-section
      [:div.container
       [:div.row.align-items-center.justify-content-center
        [:div.col-auto.mx-5.text-center.d-none.d-lg-block.d-sm-none.d-md-none
         [:img
          {:src "images/g.png"}]]
        [:div.col-md-7.col-xs-12
         [:div.section_heading
          "Gabby is free and easy to use"]
         [:div.bottom_section_text
          "This is an experiment from 3 friends that want to get 100 strangers (future friends) to go through it :) If you like hearing from us please add your email and we will make sure to keep you informed :)"]

         [mailerlite-embedded-form]]]
       [:div.row.align-items-center.justify-content-center.by-line
        [:h4 "Experiment from Toronto from 4 "
         [:span.icon-smiley-glasses "🤓"]
         " with "
         [:span.icon-heart "❤️"]]]]]]))

(defmethod routes/panels :home-panel [] [home-panel])

;; app
;; TODO put inline style in css file

(def product-categories-meta-map {:laptop {:img-src "/images/laptop.svg"
                                           :label "Laptop"}
                                  :monitor {:img-src "/images/monitor.png"
                                            :label "Monitor"}
                                  :headphone {:img-src "/images/headphone.svg"
                                              :label "Headphone"}
                                  :mouse {:img-src "/images/mouse.svg"
                                          :label "Mouse"}
                                  :tv {:img-src "/images/tv.svg"
                                       :label "TV"}})
(defn product-index-panel []
  (reagent/create-class
   {:component-did-mount
    (fn []
      (.capture js/window.posthog "$pageview")
      (re-frame/dispatch [::events/get-categories]))
    :reagent-render
    (fn []
      (let [categories-loading? @(re-frame/subscribe [::subs/categories-loading])
            active-panel @(re-frame/subscribe [::subs/get-active-panel])
            product-label @(re-frame/subscribe [::subs/product-category])
            product-categories @(re-frame/subscribe [::subs/get-product-categories])]
        [:div.container.product-flow
         {:role "main"}
         [common-header active-panel product-label]
         [:div#page1
          [:div.row.product-flow--step-heading
           [:div.col-sm
            [:div#step "Step 1"]]]
          [:div.row
           [:div.col.mx-auto
            [:div.step_instruction "Select the product you are interested in"]]]
          [:div.row.align-items-center.justify-content-center.pt-3
           [:div.col.mx-auto
            [:div.more_categories_label "We will be adding more product categories after this experiment"]]]
          [:div.product-category-list-container
           [:div.row.product-category-list
            {:class (if (true? categories-loading?) "product-category-list--loading" "")}
            (for [product-item (if (true? categories-loading?) (range 4) product-categories)]
              ^{:key product-item}
              [:div.product-category-container.col-6.col-sm-6.col-md-6.col-lg-3
               (if (true? categories-loading?)
                 [:div.product_category
                  [:div.row.justify-content-center.align-self-center
                   [:div.shimmer.shimmer--img]]
                  [:div.row.justify-content-center.align-self-center
                   [:div.product_category_label.shimmer.shimmer--label]]]
                 [:div.product_category
                  {:name product-item
                   :role "button"
                   :on-click #(re-frame/dispatch [:get-attributes product-item])} ;; TODO change to button element
                  [:div.row.justify-content-center.align-self-center
                   [:img
                    {:src (:img-src ((keyword product-item) product-categories-meta-map))}]]
                  [:div.row.justify-content-center.align-self-center
                   [:div.product_category_label (:label ((keyword product-item) product-categories-meta-map))]]])])]]]]))}))


(defmethod routes/panels :product-index-panel [] [product-index-panel])

;; product-attributes-panel

(defn product-attributes-panel []
  (reagent/create-class
   {:component-did-mount
    (fn []
      (.capture js/window.posthog "$pageview"))
    :reagent-render
    (fn []
      (let [loading? @(re-frame/subscribe [::subs/loading?])
            active-panel @(re-frame/subscribe [::subs/get-active-panel])
            device-category @(re-frame/subscribe [::subs/device-category])
            product-attributes @(re-frame/subscribe [::subs/product-attributes device-category])
            product-attributes-count @(re-frame/subscribe [::subs/product-attributes-count])
            product-label @(re-frame/subscribe [::subs/product-category])
            visible-product-attributes-count @(re-frame/subscribe [::subs/get-visible-product-attributes-count])
            product-attributes-stat "89%"] ;; TODO refer dynamically
        (if (and (nil? (js->clj loading?)) (empty? product-attributes))
          (re-frame/dispatch [::events/navigate :home])
          ;; else
          [:div.container.product-flow
           [common-header active-panel product-label]
           ;; [:h3 (str "screen-width: " @(re-frame/subscribe [::bp/screen-width]))]
           [:div#page2
            [:div.row.product-flow--step-heading
             [:div.col-sm
              [:div#step "Step 2"]]]
            [:div.row
             [:div.col.mx-auto
              [:div#step2_instruction
               "Choose "
               [:b "at least 3 options "]
               "that matter to you when buying a " [:b product-label]]]]
            [:div.row.align-items-center.justify-content-center
             {:style {:padding-top "1.5rem"}}
             [:div.col.mx-auto
              [:div#step2_attribute_stats
               "These attributes are what "
               [:span#attribute_pct.purple1 product-attributes-stat]
               " of users find important within the category."]]]
            (if (true? loading?)
              [:div.loading_shimmer_attributes_list
               [:div.align-items-center.justify-content-center.my-4
                [:div.btn-group-toggle
                 [:label.btn.attribute_tag
                  [:div.shimmer.shimmer_attribute_tag]]
                 [:label.btn.attribute_tag
                  [:div.shimmer.shimmer_attribute_tag]]
                 [:label.btn.attribute_tag.d-xs-none.d-sm-none.d-none.d-md-inline.float-left
                  [:div.shimmer.shimmer_attribute_tag]]
                 [:label.btn.attribute_tag.d-xs-none.d-sm-none.d-none.d-md-inline.float-left
                  [:div.shimmer.shimmer_attribute_tag]]]]]
              ;; Atributes lists
              [:div.attributes_list
               (for [group product-attributes]
                 ^{:key group}
                 [:div.row.align-items-center.justify-content-center
                  [:div.btn-group-toggle.px-4
                   (for [item group]
                     ^{:key item}
                     [:label.btn.attribute_tag
                      {:class (when (true? (:selected item)) "active")}
                      [:input
                       {:type "checkbox"
                        :on-change #(re-frame/dispatch [::events/update-product-attribute item])}]
                      (:phrase item)])]])])
            [:div.row.align-items-center.justify-content-center.product-attributes--show-more-btn
             (when (< visible-product-attributes-count product-attributes-count)
               [:button.col-mx-auto.show_more_attributes
                {:on-click #(re-frame/dispatch [::events/show-more-attributes visible-product-attributes-count])}
                "Show more"])]
            [:div.row.align-items-center.justify-content-center.product-attributes--continue-btn
             [:button.btn.btn_step2Continue
              {:type "button"
               :on-click #(re-frame/dispatch [::events/get-products])}
              "Continue"]]]])))}))

(defmethod routes/panels :product-attributes-panel [] [product-attributes-panel])

;; products page
(defn review-card [review]
  (let [expand? (reagent/atom false)]
    (fn []
      [:div.modal_review
       [:div.modal_review_title
        (:reviewTitle review)]
       [:p.modal-review--text
        {:class (if (true? @expand?) "--text-expanded" "--text-collapsed")}
        (:reviewText review)
        (when (not (true? @expand?))
          [:a.modal-review--more-text
           {:on-click #(reset! expand? true)}
           "...more"])]
       [:small (.toLocaleString (js/Date. (:reviewTime review)))]
       [:b.product-review-modal--filter-tag-sentiment
        {:class (case (:sentiment review)
                  "positive" "-tag-positive"
                  "negative" "-tag-negative"
                  "")}
        (case (:sentiment review)
          "positive" "Positive"
          "negative" "Negative")]])))

(defn reviews-sentiment-bar [reviews]
  (let [positive-sentiment-count @(re-frame/subscribe [::subs/count-review-sentiments {:sentiment "positive" :context reviews}])
        negative-sentiment-count @(re-frame/subscribe [::subs/count-review-sentiments {:sentiment "negative" :context reviews}])
        calc-percentage (fn [sentiment-count]
                          (str (js/Math.ceil (* 100 (/ sentiment-count (count reviews)))) "%"))]
    [:div.progress
     [:div.progress-bar.-progress-positive
      {:role "progressbar"
       :style {:width (calc-percentage positive-sentiment-count)}}]
     [:div.progress-bar.-progress-negative
      {:role "progressbar"
       :style {:width (calc-percentage negative-sentiment-count)}}]]))

;; TODO cancel apis when closing the modal, if it did not return
(defn product-reviews-modal
  "description..."
  [product]
  (let [show? (reagent/atom false)
        freeze-body #(set! (-> js/document
                               (.-body)
                               (.-style)
                               (.-overflow)) "hidden")
        reset-body-style #(set! (-> js/document
                                    (.-body)
                                    (.-style)) "")]
    (fn []
      (let [_reviews @(re-frame/subscribe [::subs/product-reviews])
            reviews-filter-context @(re-frame/subscribe [::subs/reviews-filter-context])
            _reviews-filtered @(re-frame/subscribe [::subs/filtered-reviews])
            _reviews-loading @(re-frame/subscribe [::subs/reviews-loading?])
            sentiment-filter-context @(re-frame/subscribe [::subs/get-reviews-sentiment-context])
            has-filter (> (count (filter (fn [item] (true? (last item)))  reviews-filter-context)) 0)
            has-sentiment-filter (or (:negative sentiment-filter-context) (:positive sentiment-filter-context))
            reviews (if (or has-filter has-sentiment-filter) _reviews-filtered _reviews)
            ]
        [v-box :src (at)
         :children [[:div.num_reviews
                     {:on-click (fn []
                                  (reset! show? true)
                                  (re-frame/dispatch [::events/get-reviews product])
                                  (freeze-body))}
                     "See " (:total_reviews_in_context product) " reviews"]
                    (when @show?
                      [modal-panel :src (at)
                       :backdrop-on-click (fn []
                                            (reset! show? false)
                                            (re-frame/dispatch [::events/data-remove-reviews])
                                            (reset-body-style))
                       :parts {:child-container {:class "product-reviews-modal-container"}}
                       :child [:div.product-reviews-modal--modal-content
                               [:div.modal-header.product-reviews-modal-header
                                [:h5.modal-title (:title product)]
                                [:button.close
                                 {:type "button"
                                  :aria-label "Close"
                                  :on-click (fn []
                                              (reset! show? false)
                                              (re-frame/dispatch [::events/data-remove-reviews])
                                              (reset-body-style))}
                                 [:img {:src "/images/close_icon.svg"}]]]
                               [:p.product-review-modal--sub-header.d-sm-block.d-block.d-md-none.d-lg-none.d-none
                                "Showing top " (:total_reviews_in_context product) " reviews of " (:num_reviews product) " Reviews"]
                               [:div.product-review-modal--attributes-list
                                [:div {:class "btn-group-toggle"}
                                 [:label.btn.modal_attribute_tag
                                  {:class (if (true? has-filter) "" "active")}
                                  [:input
                                   {:type "checkbox"
                                    :on-click #(re-frame/dispatch [::events/reset-filter-context])}] "All"
                                  [:span.product-review-modal--attributes-list-count " "
                                   (if _reviews-loading
                                     [:span.spinner-border.spinner-border-sm
                                      {:role "status"}
                                      [:span.sr-only "Loading..."]]
                                     (count _reviews))]]
                                 (for [item reviews-filter-context]
                                   ^{:key (first item)}
                                   [:label.btn.modal_attribute_tag
                                    {:class (if (true? (last item))
                                              "active"
                                              (if (zero? @(re-frame/subscribe [::subs/count-reviews item])) "disabled" ""))}
                                    [:input
                                     {:type "checkbox"
                                      :on-click #(re-frame/dispatch [::events/update-filter-context {:item item :context reviews-filter-context}])
                                      :disabled (if (zero? @(re-frame/subscribe [::subs/count-reviews item])) true "")}]
                                    (first item)
                                    [:span.product-review-modal--attributes-list-count " "
                                     (if _reviews-loading
                                       [:span.spinner-border.spinner-border-sm
                                        {:role "status"}
                                        [:span.sr-only "Loading..."]]
                                       @(re-frame/subscribe [::subs/count-reviews item])
                                       )]])]]
                               [:div.reviews-modal--sub-filter-group
                                [reviews-sentiment-bar reviews]
                                (when (false? _reviews-loading)
                                  (doall
                                   [:div.row.mt-3
                                    [:div.col-6
                                     [:button.reviews-modal--filter-pill-btn
                                      {:on-click #(re-frame/dispatch [::events/toggle-sentiment-filter-context :positive])
                                       :class (if (true? (:positive sentiment-filter-context)) "active" "")}
                                      [:b.-text-green "Positive"]
                                      [:span " " @(re-frame/subscribe [::subs/count-review-sentiments {:sentiment "positive" :context reviews}])]]]
                                    [:div.col-6
                                     [:button.reviews-modal--filter-pill-btn.float-right
                                      {:on-click #(re-frame/dispatch [::events/toggle-sentiment-filter-context :negative])
                                       :class (if (true? (:negative sentiment-filter-context)) "active" "")}
                                      [:b.-text-red "Negative"]
                                      [:span " " @(re-frame/subscribe [::subs/count-review-sentiments {:sentiment "negative" :context reviews}])]]]]))]
                               [:div.__modal-body

                                (when (true? _reviews-loading)
                                  (for [loading-item (range 2)]
                                    ^{:key loading-item}
                                    [:div.reviews-modal--loading-shimmer
                                     [:div.shimmer
                                      {:style {:height "18px"
                                               :margin-bottom "0.5rem"}}]
                                     [:div.shimmer
                                      {:style {:height "18px"
                                               :margin-bottom "1rem"
                                               :width "75%"}}]
                                     [:div.shimmer
                                      {:style {:height "18px"
                                               :width "20%"}}]]))
                                (when (false? _reviews-loading)
                                  [:div.modal_review_content
                                   (doall (for [review reviews]
                                            ^{:key review}
                                            [review-card review]
                                            ))])]]])]]))))
;; TODO refactor make dry
(defn product-score-class [score]
  (let [score-rounded (->> score (* 100) (Math/round))]
    (cond
      (and (> score-rounded 50) (< score-rounded 85)) "text--matching_score_med"
      (> score-rounded 85) "text--matching_score_high"
      :else "text--matching_score_low")))

(defn product-score-fn [score] (.round js/Math (* 100 score)))

(defn freeze-body []
  (set! (-> js/document
            (.-body)
            (.-style)
            (.-overflow)) "hidden"))

(defn product-matching-score-modal
  "description..."
  ;; good_battery_life_pos_pbry  / good_battery_life_num_reviews_pbry -➝ green bar
  ;; good_battery_life_neg_pbry  / good_battery_life_num_reviews_pbry -➝ red bar
  ;; good_battery_life_num_reviews  -➝ Number above the bar.. remove % sign
  ;; if 0 , then remove bar and grey out attributes texts (70% opacity)
  [product]
  (let [show? (reagent/atom false)
        reviews-loading? @(re-frame/subscribe [::subs/reviews-loading?])

        reset-body-style #(set! (-> js/document
                                    (.-body)
                                    (.-style)) "")
        selected-attributes @(re-frame/subscribe [::subs/selected-attributes])
        parse-score-level (fn [attribute-name]
                            (-> ((keyword (str attribute-name "_pbry")) product)
                                (js/Math.round)
                                (* 100)))
        parse-score-level-positive (fn [item]
                                     (let [num-reviews (:num_reviews_pbry item)
                                           pos-reviews (:pos_pbry item)]
                                       (cond
                                         (zero? num-reviews) 0 ;; don't display NaN
                                         :else (-> pos-reviews
                                                   (/ num-reviews) 
                                                   (* 100)
                                                   ))))
        parse-score-level-negative (fn [item]
                                     (let [num-reviews (:num_reviews_pbry item)
                                           neg-reviews (:neg_pbry item)]
                                       (cond
                                         (zero? num-reviews) 0 ;; don't display NaN
                                         :else (-> neg-reviews
                                                   (/ num-reviews) 
                                                   (* 100)
                                                   ))))
        product-score (fn [score] (.round js/Math (* 100 score)))]
    (fn []
      [v-box :src (at)
       :children [[:a.matching_score_header
                   {:on-click (fn []
                                (reset! show? true)
                                (freeze-body)
                                (re-frame/dispatch [::events/get-reviews product]))}
                   "Matching score"
                   [:img
                    {:src "/images/info.svg"}]
                   [:span.float-right.product-score-mobile
                    {:class (product-score-class (:score product))}
                    (product-score-fn (:score product))
                    "%"]]
                  (when @show?
                    [modal-panel :src (at)
                     :backdrop-on-click (fn []
                                          (reset! show? false)
                                          (reset-body-style))
                     :parts {:child-container {:class "product-matching-score-modal-container"}}
                     :child [:div.product-matching-score-modal--modal-content
                             [:div.modal-header
                              [:h5#score_modal_title.matching_score_modal_title.w-100
                               "Matching Score"]
                              [:button.close
                               {:type "button"
                                :aria-label "Close"
                                :on-click (fn []
                                            (reset! show? false)
                                            (re-frame/dispatch [::events/data-remove-reviews])
                                            (reset-body-style))}
                               [:img {:src "/images/close_icon.svg"}]]]
                             [:div.row.no-gutters
                              [:div.col-9.product_matchingscore_modal_subheading
                               {:style {:padding-left "1.2rem"}}
                               "This score represents the product matching based on the attributes that matters to you. Per-attribute matching scores are shown below."]
                              [:div.col-3
                               [:div.matching_score
                                [:div.matching_score_modal--circle-wrapper.float-right
                                 [:div.matching_score_modal--circle.matching_score_modal_high
                                  [:div.matching_score_modal_num
                                   (product-score (:score product)) [:span.font-style-base "%"]]]]]]] ;; TODO dynamic ref
                             [:div.matching_score_modal_body
                              [:div.matching_score_modal_body_heading.my-4
                               "Attributes"]]
                             [:div.row.matching_score_modal_body_attributescores
                              [:div.row
                               (for [item (:attributes product)]
                                 ^{:key (:name item)}
                                 [:section.col-md-6.col-xs-12.col-sm-12
                                  {:class (if (not (zero? (js/Math.round (:num_reviews item)))) "" "-off-focus")}
                                  [:div.row
                                   [:div.col-12.justify-content-between.product-matching-score-modal--attribute-list-heading
                                    [:div.product_matchingscore_modal_attribute_label (:name item)]
                                    [:div.product_matchingscore_modal_attribute_value (:num_reviews item) " mentions"]]
                                   [:div.col-12.product-matching-score-modal--sentiment-labels
                                    [:div.product-matching-score-modal--sentiment-labels.-tag-positive.float-left "Positive "
                                     [:b (parse-score-level-positive item)]]
                                    [:div.product-matching-score-modal--sentiment-labels.-tag-negative.float-right "Negative "
                                     [:b (parse-score-level-negative item)]]]
                                   (when (not (zero? (js/Math.round (:num_reviews item))))
                                     [:div.progress.product-matching-score-modal--sentiment-bar
                                      [:div.progress-bar.-progress-positive
                                       {:style {:width (str (* 100 (parse-score-level-positive item)) "%")}}]
                                      [:div.progress-bar.-progress-negative
                                       {:style {:width (str (* 100 (parse-score-level-negative item)) "%")}}]])]])]]]])]])))

(defn product-reviews-panel []
  (reagent/create-class
   {:component-did-mount
    (fn []
      ;; Posthog
      (.capture js/window.posthog "$pageview")

      ;; Typeform
      (let [el (.createElement js/document "script")]
        (.setAttribute el "src" "//embed.typeform.com/next/embed.js")
        (.setTimeout js/window #(.appendChild (.querySelector js/document ".feedback_card_ctas") el)) ;; TODO: put check if script is already added before doing appendChild
        ))
    :reagent-render
    (fn []
      (let [product-list @(re-frame/subscribe [::subs/product-list])
            products-loading? @(re-frame/subscribe [::subs/products-loading?])
            product-score (fn [score] (.round js/Math (* 100 score)))
            product-score-color (fn [score]
                                  (let [score-rounded (->> score (* 100) (Math/round))]
                                    (cond
                                      (and (> score-rounded 50) (< score-rounded 85)) "matching_score_med"
                                      (> score-rounded 85) "matching_score_high"
                                      :else "matching_score_low")))
            active-panel @(re-frame/subscribe [::subs/get-active-panel])
            product-search-result-count @(re-frame/subscribe [::subs/product-search-results-count])
            product-label @(re-frame/subscribe [::subs/product-category])]

        ;; ON LOAD: check if both products-loading? and product-list are null, then redirect to :home page
        (if (and (nil? (js->clj products-loading?)) (nil? (js->clj product-list)))
          (re-frame/dispatch [::events/navigate :home])
          ;; else
          [:div.container.product-flow
           [common-header active-panel product-label]
           [:div#page4
            [:div.row
             {:style {:padding-top "1.5rem"}}
             [:div.col.mx-auto
              [:div#step_instruction
               "Showing 10 best matched "
               [:span.title-case
                (cond
                  (= product-label "tv") "TV"
                  :else product-label)]]]]
            [:div.row.align-items-center.justify-content-center
             {:style {:padding-top "1.5rem"}}
             [:div#step4_product_stats
              "Scoured through "
              (if (not products-loading?)
                [:span#matchedProducts_count.purple1
                 product-search-result-count " products"]
                ;; else
                [:span.spinner-border.spinner-border-sm
                 {:role "status"}
                 [:span.sr-only "Loading..."]])
              " based on what best mattered to you"]]
            [:div.feedback_card
             [:div.row.align-items-center
              [:div.col-md-8.col-xs-12
               [:div.feedback_card_text
                "Done! Thank you for interacting with Gabby :)"
                [:br]
                [:b "We would really appreciate your feedback that would take you only seconds"]]]

              [:div.feedback_card_ctas.col-md-4.col-xs-12
               [:button.btn.btn_feedback
                {:data-tf-popup "XCFwhQp7"
                 :data-tf-hide-headers ""
                 :data-tf-iframe-props "title=Join Gabby - Exit Feedback Form"
                 :data-tf-medium "snippet"}
                "Provide Feedback"]]]]
            (when (true? products-loading?)
              [:div#loading_shimmer_product_list ;; TODO integrate processing indicator to actual card
               [:div.product_card
                [:div.row
                 [:div.col-3
                  [:div.shimmer
                   {:style {:height "100%"}}]]
                 [:div.col-7
                  [:div.shimmer.shimmer_small_para
                   {:style {:margin-bottom "1rem"}}]
                  [:div.row
                   [:div.col-5
                    [:div.shimmer.shimmer_small_para]]
                   [:div.col-7
                    [:div.shimmer.shimmer_small_para
                     {:style {:text-align "right"
                              :width "70%"
                              :float "right"}}]]]
                  [:div.shimmer.shimmer_large_para
                   {:style {:margin-top "1rem"}}]]
                 [:div.col-2
                  {:style {:padding-left "0"}}
                  [:div.shimmer.shimmer_small_para]
                  [:div.shimmer
                   {:style {:height "60%"
                            :margin-top "1rem"}}]]]]])
            ;; ============
            ;; PRODUCT LIST
            ;; ============
            (when (not products-loading?)
              [:div#product_list
               (doall (for [product product-list]
                        ^{:key product}
                        [:div.product_card
                         [:div.product_score_mobile
                          [product-matching-score-modal
                           product
                           (product-score (:score product))]]
                         [:div.row
                          [:div.col-md-3.col-4
                           [:div.product_image
                            [:img.img-fluid
                             {:style {:max-height "250px"}
                              :src (:imageURLHighRes product)}]]]
                          [:div.col-md-7.col-8
                           [:div.product_name
                            {:data-toggle "modal"
                             :data-target "#product_review_modal"
                             :data-asin (:asin product)
                             :data-nreviews (:num_reviews product)} (:title product)]
                           [:div.row
                            [:div.col-lg-4.col-xs-12
                             ;; [:div.num_reviews
                             ;;  {:data-toggle "modal"
                             ;;   :data-target "#product_review_modal"
                             ;;   :data-asin (:asin product)}]
                             [product-reviews-modal
                              product
                              (:num_reviews product)
                              @(re-frame/subscribe [::subs/reviews-filter-context])]]
                            [:div.col-lg-8.col-xs-12
                             [:div.product_link
                              [:a
                               {:href (str "https://www.amazon.com/dp/" (:asin product))
                                :target "_blank"
                                :rel "noopener noreferrer"} "See product on Amazon"]]]]
                           [:div.row.align-items-center.product_card_helpful
                            [:div.col-lg-7.col-sm-6
                             "Was this recommendation helpful"]
                            [:div.col-lg-4.col-sm-6
                             [:button.btn.thumbs_btn.thumbs_up.__thumbs_up_active
                              {:style {:margin-right "0.5rem"}
                               :class (if (true? (:liked product)) "thumbs_up_active" "thumbs_up_inactive")
                               :on-click #(re-frame/dispatch [::events/like product])}]
                             [:button.btn.thumbs_btn.thumbs_down.__thumbs_down_inactive
                              {:class (if (true? (:disliked product)) "thumbs_down_active" "thumbs_down_inactive")
                               :on-click #(re-frame/dispatch [::events/dislike product])}
                              ]]]]
                          [:div.col-md-2.product_score
                           {:style {:padding-left "0"}}
                           [product-matching-score-modal
                            product
                            (:num_reviews product)]
                           [:div.matching_score
                            [:div.matching_score_circle
                             [:div {:class (product-score-color (:score product))}
                              [:div.matching_score_num
                               (product-score (:score product)) [:span.font-style-base "%"]]]]]]]
                         [:div.row.align-items-center.product_card_helpful_mobile
                          [:div.col-6.text-right
                           "Was this helpful"]
                          [:div.col-6
                           [:button.btn.thumbs_btn.thumbs_up.thumbs_up_inactive
                            {:style {:margin-right "0.5rem"}
                             :class (if (true? (:liked product)) "thumbs_up_active" "thumbs_up_inactive")
                             :on-click #(re-frame/dispatch [::events/like product])}]
                           [:button.btn.thumbs_btn.thumbs_down.thumbs_down_inactive
                            {:class (if (true? (:disliked product)) "thumbs_down_active" "thumbs_down_inactive")
                             :on-click #(re-frame/dispatch [::events/dislike product])}]]]]))])]])))}))

(defmethod routes/panels :product-reviews-panel [] [product-reviews-panel])


;; main

(defn main-panel []
  (let [active-panel (re-frame/subscribe [::subs/active-panel])]
    (routes/panels @active-panel)))
