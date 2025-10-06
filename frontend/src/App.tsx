import * as React from 'react';
import Layout from './BookingLayout';
import './index.css'
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

const router = createBrowserRouter([
  {
    path: "/book",
    Component: Layout,
  },
]);


export default function DividerStack() {
  return (
    <RouterProvider router={router} />
  );
}