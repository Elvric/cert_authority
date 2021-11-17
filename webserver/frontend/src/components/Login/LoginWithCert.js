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

const forge = require("node-forge");
forge.options.usePureJavascript = true;
const asn1 = forge.asn1;

export default function Login(props){
    const [uploadFile, setUploadFile] = React.useState(null);
    const navigate = useNavigate();
    const AuthContext = AuthConsumer();
    const { state } = useLocation();

    const handleSubmit = async function (e) {
        e.preventDefault();
        const dataArray = new FormData();
        dataArray.append("uploadFile", uploadFile);
        let cert = uploadFile[0]; //file object
        var reader = new FileReader();
        var fileByteArray = [];
        reader.readAsArrayBuffer(cert);
        reader.onloadend = function (evt) {
            if (evt.target.readyState == FileReader.DONE) {
                var arrayBuffer = evt.target.result;
                var array = new Uint8Array(arrayBuffer);
                for (var i = 0; i < array.length; i++) {
                    fileByteArray.push(array[i]);
                }
                AuthContext.loginWithCert(fileByteArray).then(() => {
                  if (state !== null){
                    navigate(state);
                  }
                  else{
                    navigate("/home");
                  }
                });
            }
        };
    };

    function validateForm() {
        return (uploadFile !== null);
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
                    <Form.Control type="file" onChange={(e) => setUploadFile(e.target.files)}/>
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