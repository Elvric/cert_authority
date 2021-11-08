"use strict;"
import React, {Component, useState, useEffect} from 'react';

//BootStrap react imports

import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

import 'bootstrap/dist/css/bootstrap.min.css';

import 'whatwg-fetch';
import "./Login.css";
import Nav from "./Nav";
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import AuthConsumer from './useAuth';
import Container from 'react-bootstrap/esm/Container';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
const csrftoken = getCookie('csrftoken'); //Supposing we will use csrf tokens

export default function Login(props){
    const [user, setUser] = useState("");
    const [password, setPassword] = useState("");
    //TO DO: session management. Here is for example if we will use tokens
    const setToken = props.setToken;

    const navigate = useNavigate();
    const authContext = AuthConsumer();
    const { state } = useLocation();

    const handleSubmit = async function (e) {
        e.preventDefault();

        authContext.login().then( () => {
          navigate(state.path || "/home");
        });
    }
    
    function validateForm() {
        return user.length > 0 && password.length > 0;
    }
    
    return (
      <div className="LoginPage">
        <Container fluid>
          <Nav></Nav>
        </Container>
        <div className="Login">
          <Form onSubmit={handleSubmit}>
            
            <Form.Group size="lg" controlId="user">
              <Form.Label>UserID</Form.Label>
              
              <Form.Control
                autoFocus
                type="user"
                value={user}
                onChange={(e) => setUser(e.target.value)}
              />
            </Form.Group>
            
            <Form.Group size="lg" controlId="password">
              <Form.Label>Password</Form.Label>
              
              <Form.Control
                autoFocus
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Form.Group>
            
            <div className="LoginButton">
                <Button block variant="success" size ="lg" type="submit" disabled={!validateForm()}>
                    Login
                </Button>
            </div>
          </Form>
        </div>
      </div>
      );
}