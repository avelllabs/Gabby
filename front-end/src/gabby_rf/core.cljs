(ns gabby-rf.core
  (:require
   [reagent.dom :as rdom]
   [re-frame.core :as re-frame]
   [breaking-point.core :as bp]
   [gabby-rf.events :as events]
   [gabby-rf.routes :as routes]
   [gabby-rf.views :as views]
   [gabby-rf.config :as config]
   [day8.re-frame.http-fx]
   [re-com.core]))

(defn get-browser-navigator-vendor [app-el]
  (let [vendor (aget js/window "navigator" "vendor")]
    (.setAttribute app-el "data-navigator-vendor" vendor)))

(defn dev-setup []
  (when config/debug?
    (println "dev mode")))

(defn ^:dev/after-load mount-root []
  (re-frame/clear-subscription-cache!)
  (let [root-el (.getElementById js/document "app")]
    (get-browser-navigator-vendor root-el)
    (rdom/unmount-component-at-node root-el)
    (rdom/render [views/main-panel] root-el)))

(defn init []
  (routes/start!)
  (re-frame/dispatch-sync [::events/initialize-db])
  (re-frame/dispatch-sync [::bp/set-breakpoints
                           {:breakpoints [:mobile
                                          768
                                          :tablet
                                          992
                                          :small-monitor
                                          1200
                                          :large-monitor]
                            :debounce-ms 166}])
  (dev-setup)
  (mount-root))
