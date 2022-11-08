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
      ;; (println "I mounted")
      ;; ml.fn.renderEmbeddedForm
      ;; (let [ml "ml"
      ;;       mlfn "fn"
      ;;       mlRenderForm "renderEmbeddedForm"
      ;;       renderForm (aget js/window ml mlfn mlRenderForm)
      ;;       params #js {:yo "1"}]
      ;;   (js/console.log "jk log fn" (renderForm params)))
      (.setTimeout js/window (fn []
                               (let [ml-form (.querySelectorAll js/document ".ml-embedded")]
                                 (when (empty? (aget ml-form 0 "innerHTML")) (fetch-render-ml-form))))))

       ;; ... other methods go here
       ;; see https://facebook.github.io/react/docs/react-component.html#the-component-lifecycle
       ;; for a complete list

       ;; name your component for inclusion in error messages
    :display-name "mailerlite-embedded-form"

       ;; note the keyword for this method
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
           {:src "images/landing_img2.png"}]]
         [:div.col-sm-8.col-md-8.col-lg-5.text-left
          [:div.section_heading
           "We'll do the work"]
          [:div.section_text
           "Gabby will show you all the best products based on the features you choose"]
          [:div.row.align-items-center.justify-content-center
           [:div.col-xs-12.col-sm-12
            [:img.d-block.d-xs-block.d-sm-block.d-lg-none.d-none
             {:src "images/landing_img2.png"}]]]
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
         
         [mailerlite-embedded-form]
         [:form#subscribe-form.subscribe-form
          {:style {:display "none"}}
          [:div.row.align-items-center
           [:div.col-xs-12.col-sm-12.col-md-5.offset-md-2.mt-2
            [:label.sr-only
             {:for "inlineFormInputEmail"}
             "Email"]
            [:input
             {:type "email"
              :name "email"
              :required true
              :class "form-control"
              :id "inlineFormInputEmail"
              :placeholder "Enter email address"
              :value user-email
              :on-change (fn [ev]
                          ;;  (.log js/console "form:input" (.-value (.-target ev)) ev)
                           (re-frame/dispatch [::events/set-user-email (.-value (.-target ev))]))}]]
           [:div.col-xs-12.col-sm-12.my-2.col-md-3.text-center.mt-3
            [:button
             {:type "submit"
              :class "btn btn_submitemail"
              :on-click (fn [ev]
                          ;; (.log js/console "form:submit" user-email ">>" (.-value (.-target ev)))
                          (.preventDefault ev ev)
                          (let [no-email? (empty? user-email)]
                            (when (false? no-email?)
                              (re-frame/dispatch [::events/subscribe user-email]))))}
             "SUBSCRIBE"]]]
          (when (true? user-subscribed?)
            [:div.row.align-items-center
             [:div.col.text-center
              [:div.subscribe_complete_box
               "Thank you for signing up!"]]])]]]
               [:div.row.align-items-center.justify-content-center.by-line
                [:h4 "Experiment from Toronto from 4 "
                 [:span.icon-smiley-glasses "🤓"]
                 " with "
                 [:span.icon-heart "❤️"]]]]]]))
       
(defmethod routes/panels :home-panel [] [home-panel])

;; app
;; TODO put inline style in css file

(def product-categories [{:img-src "/images/laptop.svg"
                          :label "Laptop"}
                         {:img-src "/images/monitor.svg"
                          :label "Monitor"}
                         {:img-src "/images/headphone.svg"
                          :label "Headphones"}
                         {:img-src "/images/mouse.svg"
                          :label "Mouse"}])
(defn product-index-panel []
  (let [product-categories product-categories
        active-panel @(re-frame/subscribe [::subs/get-active-panel])
        product-label @(re-frame/subscribe [::subs/product-category])]
    [:div.container.product-flow
     {:role "main"}
     [common-header active-panel product-label]
     [:div#page1
      [:div.row
       {:style {:padding-top "4rem"}}
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
        (for [product-item product-categories]
          ^{:key product-item}
          [:div.product-category-container.col-6.col-sm-6.col-md-6.col-lg-3
           [:div.product_category
            {:name (:label product-item)
             :role "button"
             :on-click #(re-frame/dispatch [:get-attributes (:label product-item)])} ;; TODO change to button element
            [:div.row.justify-content-center.align-self-center
             [:img
              {:src (:img-src product-item)}]]
            [:div.row.justify-content-center.align-self-center
             [:div.product_category_label (:label product-item)]]]])]]]]))


(defmethod routes/panels :product-index-panel [] [product-index-panel])

;; product-attributes-panel

(defn product-attributes-panel []
  (let [loading? @(re-frame/subscribe [::subs/loading?])
        active-panel @(re-frame/subscribe [::subs/get-active-panel])
        device-category @(re-frame/subscribe [::subs/device-category])
        product-attributes @(re-frame/subscribe [::subs/product-attributes device-category])
        product-attributes-count @(re-frame/subscribe [::subs/product-attributes-count])
        product-label @(re-frame/subscribe [::subs/product-category])
        visible-product-attributes-count @(re-frame/subscribe [::subs/get-visible-product-attributes-count])
        product-attributes-stat "89%"] ;; TODO refer dynamically
    [:div.container.product-flow
     [common-header active-panel product-label]
    ;;  [:h3 (str "screen-width: " @(re-frame/subscribe [::bp/screen-width]))]
     [:div#page2
      [:div.row
       {:style {:padding-top "4rem"}}
       [:div.col-sm
        [:div#step "Step 2"]]]
      [:div.row
       {:style {:padding-top "1.5rem"}}
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
        [:div.row.align-items-center.justify-content-center.my-4
         [:div.btn-group-toggle
          [:label.btn.attribute_tag
           [:input.shimmer.shimmer_attribute_tag]]
          [:label.btn.attribute_tag
           [:input.shimmer.shimmer_attribute_tag]]
          [:label.btn.attribute_tag
           [:input.shimmer.shimmer_attribute_tag]]
          [:label.btn.attribute_tag
           [:input.shimmer.shimmer_attribute_tag]]]]]
       ;; Atributes lists 
       [:div.attributes_list
        (for [group product-attributes]
          ^{:key group}
          [:div.row.align-items-center.justify-content-center
           [:div.btn-group-toggle
            (for [item group]
              ^{:key item}
              [:label.btn.attribute_tag
               {:class (when (true? (:selected item)) "active")}
               [:input.shimmer.shimmer_attribute_tag
                {:type "checkbox"
                 :on-change #(re-frame/dispatch [::events/update-product-attribute item])}]
               (:phrase item)])]])])
      [:div.row.align-items-center.justify-content-center.product-attributes--show-more-btn
       (when (< visible-product-attributes-count product-attributes-count)
         [:button.col-mx-auto.show_more_attributes
          {:on-click #(re-frame/dispatch [::events/show-more-attributes visible-product-attributes-count])}
          "Show more"])] ;; TODO logic show more
      [:div.row.align-items-center.justify-content-center.product-attributes--continue-btn
       [:button.btn.btn_step2Continue
        {:type "button"
         :on-click #(re-frame/dispatch [::events/get-products])}
        "Continue"]]]
     ]))

(defmethod routes/panels :product-attributes-panel [] [product-attributes-panel])

;; products page

(defn product-reviews-modal
  "description..."
  [product num-reviews selected-products]
  (let [show? (reagent/atom false)]
    (fn []
      [v-box :src (at)
       :children [[:div.num_reviews
                   {:on-click (fn []
                                (reset! show? true)
                                (re-frame/dispatch [::events/get-reviews product]))}
                   "See " num-reviews " reviews"]
                  (when @show?
                    [modal-panel :src (at)
                     :backdrop-on-click (fn []
                                          (reset! show? false)
                                          (re-frame/dispatch [::events/data-remove-reviews]))
                     :parts {:child-container {:class "product-reviews-modal-container"}}
                     :child [:div.__modal-content
                             [:div.modal-header
                              [:h5.modal-title (:title product)]
                              [:button.close
                               {:type "button"
                                :aria-label "Close"
                                :on-click (fn []
                                            (reset! show? false)
                                            (re-frame/dispatch [::events/data-remove-reviews]))}
                               [:img {:src "/images/close_icon.svg"}]]]
                             [:div.product-review-modal--attributes-list
                              [:div {:class "btn-group-toggle"}
                               [:label.btn.modal_attribute_tag.active
                                [:input
                                 {:type "checkbox"}] "All"]
                               (for [item selected-products]
                                 ^{:key item}
                                 [:label.btn.modal_attribute_tag.active
                                  [:input
                                   {:type "checkbox"}] item])]]
                             [:div.reviews-modal--sub-filter-group
                              [:p
                               "Overall 78% favourable"]
                              [:div.progress
                               [:div.progress-bar.-progress-positive
                                {:role "progressbar"
                                 :style {:width "80%"}}]
                               [:div.progress-bar.-progress-negative
                                {:role "progressbar"
                                 :style {:width "100%"}}]]
                              [:div.row.mt-4
                               [:div.col-6
                                [:button.reviews-modal--filter-pill-btn
                                 [:b.-text-green "Positive"]
                                 [:span " (1,789)"]]]
                               [:div.col-6
                                [:button.reviews-modal--filter-pill-btn.float-right
                                 [:b.-text-red "Negative"]
                                 [:span " (523)"]]]]]
                             [:div.__modal-body
                              (when (true? @(re-frame/subscribe [::subs/reviews-loading?]))
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
                              (when (false? @(re-frame/subscribe [::subs/reviews-loading?]))
                                [:div.modal_review_content
                                 (doall (for [review @(re-frame/subscribe [::subs/product-reviews])]
                                          ^{:key review}
                                          [:div.modal_review
                                           [:div.modal_review_title
                                            (:reviewTitle review)]
                                           [:p.modal-review--text
                                            {:class (if (true? (:expanded review)) "--text-expanded" "--text-collapsed")}
                                            (:reviewText review)
                                            (when (not (true? (:expanded review)))
                                              [:a.modal-review--more-text
                                               {:on-click #(re-frame/dispatch [::events/toggle-expanded-review-text review])}
                                               "...more"])]
                                           [:small (.toLocaleString (js/Date. (:reviewTime review)))]]))])]]])]])))

(defn product-score-class [score]
  (let [score-rounded (->> score (* 100) (Math/round))]
    (cond
      (and (> score-rounded 50) (< score-rounded 85)) "text--matching_score_med"
      (> score-rounded 85) "text--matching_score_high"
      :else "text--matching_score_low")))

(defn product-matching-score-modal
  "description..."
  [product product-score]
  (let [show? (reagent/atom false)
        reviews-loading? @(re-frame/subscribe [::subs/reviews-loading?])]
    (fn []
      [v-box :src (at)
       :children [[:a.matching_score_header
                   {:on-click (fn []
                      (reset! show? true)
                      (re-frame/dispatch [::events/get-reviews product]))}
                   "Matching score"
                   [:img
                    {:src "/images/info.svg"}]
                   [:span.float-right.product-score-mobile
                    {:class (product-score-class (:score product))}
                    product-score
                    "%"]]
                  (when @show?
                    [modal-panel :src (at)
                     :backdrop-on-click #(reset! show? false)
                     :parts {:child-container {:class "product-matching-score-modal-container"}}
                     :child [:div.modal-content
                             [:div.modal-header.text-center
                              [:h5#score_modal_title.matching_score_modal_title.w-100 
                               "Matching Score"]]
                             [:div.row.no-gutters
                              [:div.col-9.product_matchingscore_modal_subheading
                               {:style {:padding-left "1.2rem"}}
                               "This score represents the product matching based on the attributes that matters to you. Per-attribute matching scores are shown below."]
                              [:div.col-3
                               [:div.matching_score
                                [:div.matching_score_modal_circle
                                 [:div.matching_score_modal_high
                                  [:div.matching_score_modal_num
                                   "87%"]]]]]] ;; TODO dynamic ref
                             [:div.matching_score_modal_body
                              [:div.matching_score_modal_body_heading.my-4
                               "Attributes"]]
                             [:div.row.matching_score_modal_body_attributescores
                              [:div.col
                               {:style {:margin-right "0.5rem"}}
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]]
                              [:div.col
                               {:style {:margin-right "0.5rem"}}
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]
                               [:div.row.justify-content-between
                                [:div.product_matchingscore_modal_attribute_label "Attributes"]
                                [:div.product_matchingscore_modal_attribute_value "92%"]]]]]])]])))

(defn product-reviews-panel []
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
        product-search-result-count (.floor js/Math (+ 3000 (* (+ 1 (- 7000 3000)) (.random js/Math))))
        product-label @(re-frame/subscribe [::subs/product-category])]
    ((fn []
       (let [el (.createElement js/document "script")]
         (.setAttribute el "src" "//embed.typeform.com/next/embed.js")
         (.setTimeout js/window #(.appendChild (.querySelector js/document ".feedback_card_ctas") el)) ;; TODO: put check if script is already added before doing appendChild
         )))
    [:div.container.product-flow
     [common-header active-panel product-label]
     [:div#page4
      [:div.row
       {:style {:padding-top "1.5rem"}}
       [:div.col.mx-auto
        [:div#step_instruction
         "Showing 10 best matched products"]]]
      [:div.row.align-items-center.justify-content-center
       {:style {:padding-top "1.5rem"}}
       [:div
        (when (true? products-loading?)
          [:div.text-center.mb-4
           [:div.spinner-border.spinner-border-sm
            {:role "status"}
            [:span.sr-only "Loading..."]]])
        (when (not products-loading?)
          [:div#step4_product_stats
           "Scoured through "
           [:span#matchedProducts_count.purple1
            product-search-result-count " products"]
           " based on what best mattered to you"])]]
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
                        @(re-frame/subscribe [::subs/selected-products])]]
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
                       [:button.btn.thumbs_btn.thumbs_up.thumbs_up_inactive
                        {:style {:margin-right "0.5rem"}}]
                       [:button.btn.thumbs_btn.thumbs_down.thumbs_down_inactive]]]]
                    [:div.col-md-2.product_score
                     {:style {:padding-left "0"}}
                     ;; Matching score modal
                    ;;  [:div.matching_score_header
                    ;;   "Matching score"
                    ;;   [:img
                    ;;    {:style {:width "15px"
                    ;;             :margin-left "0.25rem"
                    ;;             :padding-bottom "3px"
                    ;;             :cursor "pointer"}
                    ;;     :src "images/info.svg"
                    ;;     :data-toggle "modal"
                    ;;     :data-target "#product_matchingscore_modal"
                    ;;     :data-matchingscore "1"
                    ;;     :data-matchinglevel "high"
                    ;;     :data-selectedattributes ""
                    ;;     :data-attributescores ""}]]
                     [product-matching-score-modal
                      product
                      (:num_reviews product)
                      @(re-frame/subscribe [::subs/selected-products])]
                     [:div.matching_score
                      [:div.matching_score_circle
                       [:div {:class (product-score-color (:score product))}
                        [:div.matching_score_num
                         (product-score (:score product)) "%"]]]]]]
                   [:div.row.align-items-center.product_card_helpful_mobile
                    [:div.col-6.text-right
                     "Was this helpful"]
                    [:div.col-6
                     [:button.btn.thumbs_btn.thumbs_up.thumbs_up_inactive
                      {:style {:margin-right "0.5rem"}}]
                     [:button.btn.thumbs_btn.thumbs_down.thumbs_down_inactive]]]]))])]]))

(defmethod routes/panels :product-reviews-panel [] [product-reviews-panel])


;; main

(defn main-panel []
  (let [active-panel (re-frame/subscribe [::subs/active-panel])]
    (routes/panels @active-panel)))
