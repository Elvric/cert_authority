"use strict;"
import React, {Component, useState, useEffect} from 'react';

//BootStrap react imports

import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

import 'bootstrap/dist/css/bootstrap.min.css';

import 'whatwg-fetch';
import "./Login.css";
import Nav from "../Nav";
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import AuthConsumer from '../useAuth';
import Container from 'react-bootstrap/esm/Container';

export default function Login(props){

    const navigate = useNavigate();
    const AuthContext = AuthConsumer();
    const { state } = useLocation();

    const handleSubmit = async function (e) {
        e.preventDefault();

        AuthContext.login().then( () => {
          if (state !== null){
            navigate(state);
          }
          else{
            navigate("/home");
          }
        });
    }
    
    return (
        <div className="LoginPage">
            <Container fluid>
                <Nav certificate={true}></Nav>
            </Container>

            <div className="Login">            
                <Form onSubmit={handleSubmit}>

                <Form.Group controlId="formFile" className="mb-3">
                    <Form.Label>Upload your certificate here</Form.Label>
                    <Form.Control type="file" />
                </Form.Group>

                </Form>
            </div>
        </div>
      );
}