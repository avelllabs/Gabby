(ns gabby-rf.subs
  (:require
   [re-frame.core :as re-frame]
   [gabby-rf.db :as db]))

(re-frame/reg-sub
 ::user-email
 (fn [db]
   (:user-email db)))

(re-frame/reg-sub
 ::subscribed?
 (fn [db]
   (:user-subscribed? db)))

(re-frame/reg-sub
 ::get-active-panel
 (fn [db]
   (.log js/console db)
   (:active-panel db)))

(re-frame/reg-sub
 ::loading?
 (fn [db]
  (:loading? db)))

(re-frame/reg-sub
 ::reviews-loading?
 (fn [db]
   (:reviews-loading? db)))

(re-frame/reg-sub
 ::product-category
 (fn [db]
   (:product-category db)))

(re-frame/reg-sub
 ::products-loading?
 (fn [db]
   (:products-loading? db)))

(re-frame/reg-sub
 ::device-category
 (fn [{bp :breaking-point.core/breakpoints}]
   (if (< (:screen-width bp) 650)
     :mobile
     :desktop)))

(defn partition-count [count device-category]
  (if (= device-category :desktop)
    (case count
     4 5
     5 4)
    (case count
      3 3
      5 3)))

(defn partition-attr [pcount parsed-attrs attrs device-category]
  (let [pcount! (partition-count pcount device-category)]
    ;; (.log js/console "p-attr>>" parsed-attrs)
    (if (zero? (count attrs))
      parsed-attrs
      (partition-attr pcount! (cons (take pcount! attrs) parsed-attrs) (drop pcount! attrs) device-category))))

(re-frame/reg-sub
 ::product-attributes-count
 (fn [db [_ params]]
  ;;  (.log js/console "::p-attrs" db ">>" params)
  ;;  (.log js/console "::product-attributes" (partition-attr 5 [] (:data-get-attributes db)) "all>>" (:data-get-attributes db))
   (count (partition-attr 5 [] (:data-get-attributes db) params))))

(re-frame/reg-sub
 ::product-attributes
 (fn [db [_ params]]
   (take (:visible-attributes db) (reverse (partition-attr 5 [] (:data-get-attributes db) params)))))

(re-frame/reg-sub
 ::selected-products
 (fn [db]
   (->> (:data-get-attributes db)
        (filterv (fn [x]
                   (when (true? (:selected x)) x)))
        (mapv (fn [x]
                (:phrase x))))))

(re-frame/reg-sub
 ::product-list
 (fn [db]
  ;;  (.log js/console ":product-list" db)
   (:data-get-products db)))

(re-frame/reg-sub
 ::active-panel
 (fn [db _]
   (:active-panel db)))

(re-frame/reg-sub
 ::product-reviews
 (fn [db]
   (:data-get-reviews db)))

(re-frame/reg-sub
 ::get-visible-product-attributes-count
 (fn [db]
   (:visible-attributes db)))

(re-frame/reg-sub
 ::get-product-categories
 (fn [db]
   (:data-get-categories db)))

(re-frame/reg-sub
 ::filtered-reviews
 (fn [db]
   (let [filter-context (->> (mapv (fn [item] (when (true? (last item)) [(first item)])) (:reviews-filter-context db))
                             (filterv some?))
         reviews (:data-reviews-grouped db)
         all-reviews-grouped-by-sentiment (group-by :sentiment (:data-get-reviews db))
         sentiment-context (:reviews-sentiment-filter-context db)
         reviews-grouped-by-sentiment (group-by :sentiment (mapcat reviews filter-context))]
    ;;  (js/console.log "::subs/filtered-reviews" "empty?" (empty? filter-context) "positive:true?" (true? (:positive sentiment-context)) "negative:false?" (false? (:negative sentiment-context)) ">" sentiment-context ">>" all-reviews-grouped-by-sentiment ">>>" (mapcat all-reviews-grouped-by-sentiment ["negative"]))
    ;;  (:data-reviews-filtered db)
     (cond
       (and (empty? filter-context) (true? (:positive sentiment-context)) (false? (:negative sentiment-context))) (mapcat all-reviews-grouped-by-sentiment ["positive"])
       (and (empty? filter-context) (false? (:positive sentiment-context)) (true? (:negative sentiment-context))) (mapcat all-reviews-grouped-by-sentiment ["negative"])
       (and (empty? filter-context) (true? (:positive sentiment-context)) (true? (:negative sentiment-context))) (:data-get-reviews db)
       (and (true? (:positive sentiment-context)) (false? (:negative sentiment-context))) (mapcat reviews-grouped-by-sentiment ["positive"])
       (and (false? (:positive sentiment-context)) (true? (:negative sentiment-context))) (mapcat reviews-grouped-by-sentiment ["negative"])
       :else (mapcat reviews filter-context)))))

(re-frame/reg-sub
 ::reviews-filter-context
 (fn [db]
  ;;  (js/console.log "::subs/reviews-filter-context" (:reviews-filter-context db))
   (:reviews-filter-context db)))

(re-frame/reg-sub
 ::get-reviews-sentiment-context
 (fn [db]
   (:reviews-sentiment-filter-context db)))

(re-frame/reg-sub
 ::count-reviews
 (fn [db [_ param]]
  ;;  (js/console.log "::subs/count-reviews" param)
   (count (get-in db [:data-reviews-grouped [(first param)]]))))

(re-frame/reg-sub
 ::count-review-sentiments
 (fn [db [_ {:keys [sentiment context]}]]
  ;;  (js/console.log "::subs/count-review-sentiments 000" sentiment (-> (group-by :sentiment context)
  ;;                                                             (keep [sentiment])
  ;;                                                             (flatten)
  ;;                                                             ))
   (let [filter-context (->> (mapv (fn [item] (when (true? (last item)) [(first item)])) (:reviews-filter-context db))
                             (filterv some?))
         reviews-context (if (empty? filter-context)
                           (:data-get-reviews db)
                           (-> (:data-reviews-grouped db)
                               (keep filter-context)
                               (flatten)))
         sentiment-context (:reviews-sentiment-filter-context db)]
    ;;  (js/console.log "::subs/count-review-sentiments 001" filter-context ">>" reviews-context ">>>" (some true? (vals sentiment-context)))
     (-> (group-by :sentiment reviews-context)
         (keep [sentiment])
         (flatten)
         (count)))))

(re-frame/reg-sub
 ::categories-loading
 (fn [db]
   (:categories-loading? db)))

(re-frame/reg-sub
 ::selected-attributes
 (fn [db]
   (:selected-attributes db)))
