import { createApp } from "vue";
import { VueQueryPlugin } from "@tanstack/vue-query";
import router from "./router";
import App from "./App.vue";
import "./styles.css";

createApp(App).use(VueQueryPlugin).use(router).mount("#root");
