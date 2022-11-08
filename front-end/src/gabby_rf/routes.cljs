(ns gabby-rf.routes
  (:require
   [bidi.bidi :as bidi]
   [pushy.core :as pushy]
   [re-frame.core :as re-frame]
   [gabby-rf.events :as events]))

(defmulti panels identity)
(defmethod panels :default [] [:div "No panel found for this route."])

(def routes
  (atom
    ["/" {
          ""      :home
          "products/" {"" :product-index
                      [:produit] :dynamic
                      [:produit "/attributes"] :product-attributes
                      [:produit "/reviews"] :product-reviews}}]))

(defn parse
  [url]
  (bidi/match-route @routes url))

(defn url-for
  [& args]
  (let [params (if (seq? args) (first args) args) ;; handle url params https://github.com/juxt/bidi
        normalize-params (if (keyword? params) (conj '() params) params)] ;; ensure all keyword only are all wrapped as a list
    (apply bidi/path-for (into [@routes] normalize-params))))

(defn dispatch
  [route]
  (let [panel (keyword (str (name (:handler route)) "-panel"))]
    (re-frame/dispatch [::events/set-active-panel panel])))

(defonce history
  (pushy/pushy dispatch parse))

(defn navigate!
  [handler]
  (pushy/set-token! history (url-for handler)))

(defn start!
  []
  (pushy/start! history))

(re-frame/reg-fx
  :navigate
  (fn [handler]
    (navigate! handler)))
