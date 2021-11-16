import { useNavigate } from "react-router-dom";
import AuthConsumer from "./useAuth";
import React, { useState, useEffect } from "react";
//BootStrap react imports
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";
import FormGroup from "react-bootstrap/FormGroup";
import Button from "react-bootstrap/Button";
import Nav from "./Nav";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Modal from "react-bootstrap/Modal";
import ModalTitle from "react-bootstrap/ModalTitle";
import ModalHeader from "react-bootstrap/ModalHeader";
import ModalBody from "react-bootstrap/ModalBody";
import ModalFooter from "react-bootstrap/ModalFooter";
import "bootstrap/dist/css/bootstrap.min.css";

import { saveAs } from 'file-saver';
import { Buffer } from "buffer";
import { copyFileSync } from "fs";
const axios = require("axios").default;

function b64_to_utf8( str ) {
  return decodeURIComponent(escape(window.atob( str )));
}

function EditModal(props) {
  const handleChange = (e) => {
    props.setField(e.target.value);
  };
  const handleSubmit = async function (e) {
    console.log("submit");
    let uid = props.user.UserId;
    let password = props.user.Password;
    let firstName = props.user.FirstName;
    let lastName = props.user.LastName;
    let email = props.user.Email;
    if (props.type === "User ID") {
      uid = props.field;
    }
    if (props.type === "Password") {
      password = props.field;
    }
    if (props.type === "First Name") {
      firstName = props.field;
    }
    if (props.type === "Last Name") {
      lastName = props.field;
    }
    if (props.type === "Email") {
      email = props.field;
    }
    props.setUser({
      UserId: uid,
      Password: "****",
      FirstName: firstName,
      LastName: lastName,
      Email: email,
    });
    props.setShow(false);
  };
  return (
    <Modal show={props.show} onHide={() => props.setShow(false)}>
      <ModalHeader closeButton>
        <ModalTitle>Edit {props.type}</ModalTitle>
      </ModalHeader>
      <ModalBody>
        <Form>
          <Form.Group
            className="mb-3"
            controlId={props.type === "Password" ? "password" : "user"}
          >
            <Form.Label>{props.type}</Form.Label>
            <Form.Control
              type={props.type === "Password" ? "password" : "user"}
              rows={1}
              placeholder={""}
              value={props.field}
              onChange={handleChange}
            />
          </Form.Group>
        </Form>
      </ModalBody>
      <ModalFooter>
        <Button color="primary" onClick={handleSubmit}>
          Save
        </Button>
      </ModalFooter>
    </Modal>
  );
}
export default function Home() {
  const AuthContext = AuthConsumer();
  //states for the modal for editing
  const [user, setUser] = useState({
    UserId: "uid",
    Password: "****",
    FirstName: "Ciro",
    LastName: "Immobile",
    Email: "ciro.immobile@lazio.it",
  });
  const [field, setField] = useState("");
  const [show, setShow] = useState(false);
  const [type, setType] = useState("");

  async function requestCertificate(e){
    e.preventDefault();
    try{
      const res = await axios.get("/api/certificate");
      if (res.status == 200){
        let data = Buffer.from(res.data.pkcs12, 'base64');
        
        saveAs(str, "cert.p12");
        window.alert("You can download your certificate!");
      }
    }
    catch(err){
      window.alert("Error!")
    }
  }
  
  return (
    <div className="HomePage">
      <Nav />
      <Container className="pt-2 pr-5 mt-5 mr-5">
        <Row className="pt-1">
          <Col>User ID: </Col>
          <Col>{user.UserId}</Col>
          <Col>
            <Button
              variant="success"
              onClick={() => {
                setField(user.UserId);
                setShow(true);
                setType("User ID");
              }}
            >
              Edit
            </Button>
          </Col>
        </Row>
        <Row className="pt-1">
          <Col>Password: </Col>
          <Col>{user.Password}</Col>
          <Col>
            <Button
              variant="success"
              onClick={() => {
                setField(user.Password);
                setShow(true);
                setType("Password");
              }}
            >
              Edit
            </Button>
          </Col>
        </Row>
        <Row className="pt-1">
          <Col>First Name: </Col>
          <Col>{user.FirstName}</Col>
          <Col>
            <Button
              variant="success"
              onClick={() => {
                setField(user.FirstName);
                setShow(true);
                setType("First Name");
              }}
            >
              Edit
            </Button>
          </Col>
        </Row>
        <Row className="pt-1">
          <Col>Last Name: </Col>
          <Col>{user.LastName}</Col>
          <Col>
            <Button
              variant="success"
              onClick={() => {
                setField(user.LastName);
                setShow(true);
                setType("Last Name");
              }}
            >
              Edit
            </Button>
          </Col>
        </Row>
        <Row className="pt-1">
          <Col>Email: </Col>
          <Col>{user.Email}</Col>

          <Col>
            <Button
              variant="success"
              onClick={() => {
                setField(user.Email);
                setShow(true);
                setType("Email");
              }}
            >
              Edit
            </Button>
          </Col>
        </Row>
      </Container>
      <Container className="pt-1 pr-5 m-5 d-flex justify-content-end">
        <Button variant="primary" onClick={requestCertificate}>Request New Certificate</Button>
      </Container>
      <EditModal
        field={field}
        setField={setField}
        user={user}
        setUser={setUser}
        show={show}
        setShow={setShow}
        type={type}
      />
    </div>
  );
}
