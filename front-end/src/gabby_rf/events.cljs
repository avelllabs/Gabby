(ns gabby-rf.events
  (:require [ajax.core :as ajax]
            [clojure.string :refer [index-of]]
            [day8.re-frame.tracing :refer-macros [fn-traced]]
            [gabby-rf.db :as db]
            [re-frame.core :as re-frame]
            [clojure.string :as str]))

(re-frame/reg-event-db
 ::initialize-db
 (fn-traced [_ _]
            db/default-db))

(re-frame/reg-event-fx
 ::navigate
 (fn-traced [_ [_ handler]]
            {:navigate handler}))

(re-frame/reg-event-fx
 ::set-active-panel
 (fn-traced [{:keys [db]} [_ active-panel]]
            {:db (assoc db :active-panel active-panel)}))


;; /getCategories
(re-frame/reg-event-db
 :get-categories-on-response-success
 (fn [db [_ response]]
  ;;  (.log js/console db response)
   (-> db
       (assoc :loading? false)
       (assoc :data-get-categories (js->clj response)))))

(re-frame/reg-event-db
 :get-categories-on-response-failure
 (fn [db [_ response]]
   ;; TODO handle failure
   ;; (.log js/console "failure" db response)
   (-> db
       (assoc :loading? false))))

(re-frame/reg-event-fx
 ::get-categories
 ;; https://joingabby.com/getCategories
 ;; GET
 (fn [{db :db} _]
   ;;(.log js/console {:db db :p params})
   {:http-xhrio {:method :get
                 :uri "https://gabby-f6171.uc.r.appspot.com/getCategories"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :format (ajax/json-request-format)
                 :on-success [:get-categories-on-response-success]
                 :on-failure [:get-categories-on-response-failure]}
    :db (-> db
            (assoc :loading? true))}))

;; /getAttributes

(re-frame/reg-event-db
 :get-attributes-on-response-success
 (fn [db [_ response]]
  ;;  (.log js/console db response)
   (-> db
       (assoc :loading? false)
       (assoc :data-get-attributes (js->clj response)))))

(re-frame/reg-event-db
 :get-attributes-on-response-failure
 (fn [db [_ response]]
   ;; TODO handle failure
   ;; (.log js/console "failure" db response)
   (-> db
       (assoc :loading? false))))

(re-frame/reg-event-fx
 :get-attributes
 ;; https://joingabby.com/getAttributes
 ;; POST
 ;; category string
 (fn [{db :db} params]
   (.log js/console "jk debug /getAttributes" {:db db :p params} (last params))
   {:http-xhrio {:method :post
                 :uri "https://gabby-f6171.uc.r.appspot.com/getAttributes"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :format (ajax/json-request-format)
                 :params {:category (str/lower-case (last params))}
                 :on-success [:get-attributes-on-response-success]
                 :on-failure [:get-attributes-on-response-failure]}
    :db (-> db
            (assoc :loading? true)
            (assoc :product-category (last params)))
    :navigate [:product-attributes :produit (last params)]}))

(re-frame/reg-event-db
 ::update-product-attribute
 (fn [db [_ product-attribute]]
   (if (true? (:selected product-attribute))
     (assoc-in db [:data-get-attributes (index-of (:data-get-attributes db) product-attribute)] (dissoc product-attribute :selected))
     (assoc-in db [:data-get-attributes (index-of (:data-get-attributes db) product-attribute)] (assoc product-attribute :selected true)))))


;; /getProducts

(re-frame/reg-event-db
 :get-products-on-response-success
 (fn [db [_ response]]
  ;;  (.log js/console db response)
   (-> db
       (assoc :products-loading? false)
       (assoc :data-get-products (js->clj response)))))

(re-frame/reg-event-db
 :get-products-on-response-failure
 (fn [db [_ response]]
  ;;  (.log js/console "failure" db response)
   (-> db
       (assoc :products-loading? false))))

(re-frame/reg-event-fx
 ::get-products
 ;; https://joingabby.com/getProducts
 ;; POST
 ;; attributes [attribute]

 ;; 
 [(re-frame/inject-cofx :get-products-params)]
 
 ;;
 (fn [{:keys [db products-params]} _]
   (.log js/console "jk debug /getProducts" products-params  {:db db})
   {:http-xhrio {:method :post
                 :uri "https://gabby-f6171.uc.r.appspot.com/getProducts"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :format (ajax/json-request-format)
                 :params {:attributes products-params
                          :category (str/lower-case (:product-category db))}
                 :on-success [:get-products-on-response-success]
                 :on-failure [:get-products-on-response-failure]}
    :db (-> db
            (assoc :products-loading? true)
            (assoc :chosen-products products-params))
    :navigate [:product-reviews :produit (:product-category db)]}))

(re-frame/reg-cofx
 :get-products-params
 (fn [cofx]
   (assoc cofx :products-params (->> (:data-get-attributes (:db cofx))
                                     (filterv (fn [x]
                                                (when (true? (:selected x)) x)))
                                     (mapv (fn [x]
                                             (:phrase x)))))))


;; /getReviews
(re-frame/reg-event-db
 :get-reviews-on-response-success
 (fn [db [v response]]
  ;;  (.log js/console ":get-reviews-on-response-success" response ">>" v)
   (-> db
       (assoc :reviews-loading? false)
       (assoc :data-get-reviews (js->clj response))
       (assoc :data-reviews-grouped (group-by :phrase (js->clj response)))
       (assoc :reviews-sentiment-filter-context {:positive false :negative false}))))

(re-frame/reg-event-db
 :get-reviews-on-response-failure
 (fn [db [_ _]]
   (js/console.error ":get-reviews-on-response-failure")
   (-> db
       (assoc :reviews-loading? false))))

(re-frame/reg-event-fx
 ::get-reviews
  ;; https://joingabby.com/getReviews
  ;; POST
  ;; payload {"asin":"B0148NNKTC","attributes":["the display","this issue","these monitors"]}

 [(re-frame/inject-cofx :get-products-params)]

 ;;
 (fn [{:keys [db products-params]} [_ product]]
  ;;  (.log js/console "::subs/get-reviews" product (:product-category db))
   {:http-xhrio {:method :post
                 :uri "https://gabby-f6171.uc.r.appspot.com/getReviews"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :format (ajax/json-request-format)
                 :params {:attributes products-params
                          :asin (:asin product)
                          :category (str/lower-case (:product-category db))}
                 :on-success [:get-reviews-on-response-success]
                 :on-failure [:get-reviews-on-response-failure]}
    :db (-> db
            (assoc :reviews-loading? true)
            (assoc :reviews-filter-context (mapv (fn [item] [item false]) (:chosen-products db))))}))

(re-frame/reg-event-db
 ::data-remove-reviews
 (fn [db _]
   (-> db
       (assoc :data-get-reviews [])
       (assoc :data-reviews-grouped {}))))

;; /subscribe
;; DEPRECATED - REMOVE IMPLEMENTATION
(re-frame/reg-event-db
 :gabby-subscribe-on-response-success
 (fn [db [_ _]]
   (js/setTimeout #(re-frame/dispatch [::reset-subscribe-success-status]) 3000)
   (-> db
       (assoc :subscribe-loading? false)
       (assoc :user-subscribed? true))))

(re-frame/reg-event-db
 :gabby-subscribe-on-response-failure
 (fn [db [_ _]]
   (-> db
       (assoc :subscribe-has-error? true)
       (assoc :subscribe-loading? false))))

;; (re-frame/reg-event-fx
;;  ::reset-subscribe-error-context
;;  (fn [{db :db} [_ _]]
;;    {:db (assoc db :subscribe-has-error? true)}))

(re-frame/reg-event-db
 ::reset-subscribe-success-status
 (fn [db [_ _]]
  ;;  (.log js/console "::reset-subscribe-success-status" db)
   (assoc db :user-subscribed? false)))

;; POST
;; payload email=u%40co.co&signup_date=2022-10-09+18%3A02%3A09+GMT%E2%88%9204%3A00+%5BAmerica%2FToronto%5D
;; form data
;; email: 
;; u@co.co
;; signup_date: 
;; 2022-10-09 18:02:09 GMT−04:00 [America/Toronto]
(re-frame/reg-event-fx
 ::subscribe
 [(re-frame/inject-cofx :get-signup-date)]

 (fn [{:keys [db signup-date]} [_ email]]
  ;;  (.log js/console "::events/subscribe" signup-date ">>" email)
   {:http-xhrio {:method :post
                 :uri "/subscribe"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :format (ajax/url-request-format)
                 :params {:email email :signup-date signup-date}
                 :on-success [:gabby-subscribe-on-response-success]
                 :on-failure [:gabby-subscribe-on-response-failure]}
    :db (-> db
            (assoc :subscribe-loading? true)
            (assoc :user-email ""))}))

(re-frame/reg-cofx
 :get-signup-date
 (fn [cofx]
   (let [p (clj->js {:timeZoneName "longOffset"})
         d (-> (js/Date.)
               (.toLocaleString "sv" p))
         tz (.-timeZone (.resolvedOptions (.DateTimeFormat js/Intl)))]
     (assoc cofx :signup-date (str d " [" tz "]")))))


(re-frame/reg-event-fx
 ::show-more-attributes
 (fn [{db :db} [_ count]]
   {:db (-> db
            (assoc :visible-attributes (+ 3 count)))}))


(re-frame/reg-event-db
 ::toggle-expanded-review-text
 (fn [db [_ review-record]]
  ;;  (.log js/console "::toggle-expanded-review-text" db ">>" review-record)
  ;;  (.log js/console "::toggle" (:data-get-reviews db) ">>" (:reviewerID review-record) ">>>" (index-of (:data-get-reviews db) review-record))
   (assoc-in db [:data-get-reviews (index-of (:data-get-reviews db) review-record)] (assoc review-record :expanded true))))

(re-frame/reg-event-db
 ::like
 (fn [db [_ param]]
   (assoc-in db [:data-get-products (index-of (:data-get-products db) param)] (merge param {:liked true :disliked false}))
   ))

(re-frame/reg-event-db
 ::dislike
 (fn [db [_ param]]
   (assoc-in db [:data-get-products (index-of (:data-get-products db) param)] (merge param {:disliked true :liked false}))
   ))

(re-frame/reg-event-fx
 ::update-filter-context
 (fn [{:keys [db]} [_ {:keys [item context]}]]
   (let [attribute (first item)
         active (last item)]
     {:db (-> db
              (assoc-in [:reviews-filter-context (index-of (:reviews-filter-context db) item)] [attribute (if (true? active) false true)]))})))

(re-frame/reg-event-db
 ::reset-filter-context
 (fn [db _]
   (assoc db :reviews-filter-context (mapv (fn [item] [(first item) false]) (:reviews-filter-context db)))))

(re-frame/reg-event-db
 ::toggle-sentiment-filter-context
 (fn [db [_ param]]
   (assoc-in db [:reviews-sentiment-filter-context param] (if (true? (get-in db [:reviews-sentiment-filter-context param])) false true))))