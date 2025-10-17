import * as React from 'react';
import Layout from './BookingLayout';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { createRoot } from 'react-dom/client'
import './index.css'
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import Resources from './components/Resources';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const router = createBrowserRouter([
  {
    path: "/:companySlug",
    Component: Layout,
    children: [
      { index: true, Component: Resources },
    ]
  },
]);

// const Item = styled(Paper)(({ theme }) => ({
//   backgroundColor: '#d61212ff',
//   ...theme.typography.body2,
//   padding: theme.spacing(1),
//   textAlign: 'center',
//   color: (theme.vars ?? theme).palette.text.secondary,
//   ...theme.applyStyles('dark', {
//     backgroundColor: '#000000ff',
//   }),
// }));

export default function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  );
}