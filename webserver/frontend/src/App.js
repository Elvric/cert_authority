import "./App.css";
import React, { useState, useEffect} from 'react';
//BootStrap react imports
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import NavLink from 'react-bootstrap/NavLink';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'whatwg-fetch';
import Login from "./components/Login";
import { Link, Routes, Route } from "react-router-dom";


function App() {
  return (
    <div className="App">
      <Container>
        <Navbar sticky="top" variant="light" bg="light">
          <Container fluid className="d-flex justify-content-between">
              <Navbar.Brand href="#home">
                  <img
                    src="imovies.png"
                    width="30"
                    height="30"
                    className="d-inline-block align-top"
                    alt="IMovies"
                  />
                  IMovies
              </Navbar.Brand>
              <Button variant="outline-secondary">Login with Certificate</Button>
          </Container>
        </Navbar>
      </Container>
      {/* Body */}
      <Container fluid className="mt-2">
        <Row className="d-flex flex-row">
          <Login>

          </Login>
        </Row>
      </Container>
    </div>
  );
}

export default App;
