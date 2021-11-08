import "./App.css";
import React, { useState, useEffect} from 'react';
//BootStrap react imports
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'whatwg-fetch';
import Login from "./components/Login/Login";
import PrivateRoute from "./components/PrivateRoute";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Routes,
} from 'react-router-dom';
import { AuthProvider, AuthConsumer } from "./components/useAuth";

//Components
const Home = () => <h1>Home</h1>;
const Certificate = () => <h1>Certificate</h1>;
const Admin = () => <h1>Admin</h1>
const NotFound = () => <h1>404: Page not found on this server</h1>

//Routes
const routes = [
  {path:"/login", component: Login, protected: false},
  {path:"/certificate", component: Certificate, protected: true},
  {path: "/admin", component: Admin, protected: true},
  {path:"/home", component: Home, protected: true},
  {path: "/*", component: NotFound, protected: false}
]

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <Router>
          <Routes>
              {routes.map((route) => (
                route.protected === true 
                  ? (<Route path={route.path} element={
                      (<PrivateRoute path={route.path}>
                        < route.component/>
                      </PrivateRoute>)
                      }/>) 
                  : (<Route path={route.path} element={<route.component/>}/>)
              ))}
          </Routes>
         </Router>
      </AuthProvider>
    </div>
  );
}

export default App;
