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