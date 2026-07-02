import React from "react";
import ReactDOM from "react-dom/client";

import { FluentProvider } from "@/components/fluent";

import { App } from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <FluentProvider>
      <App />
    </FluentProvider>
  </React.StrictMode>
);
