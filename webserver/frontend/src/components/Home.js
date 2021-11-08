import { useNavigate } from 'react-router-dom';
import AuthConsumer from './useAuth';
import React, { useState, useEffect} from 'react';
//BootStrap react imports
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import FormGroup from 'react-bootstrap/FormGroup';
import Button from 'react-bootstrap/Button';
import Nav from "./Nav";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Modal from 'react-bootstrap/Modal';
import ModalTitle from 'react-bootstrap/ModalTitle';
import ModalHeader from 'react-bootstrap/ModalHeader';
import ModalBody from 'react-bootstrap/ModalBody';
import ModalFooter from 'react-bootstrap/ModalFooter';
import 'bootstrap/dist/css/bootstrap.min.css';

function EditModal(props){
    const field = {...props.field};

    const handleChange = (e) => {
        props.setField(e.target.value);
    }
    const handleSubmit = async function (e) {
        console.log("submit");
    }
    return (
            <Modal show={props.show} onHide={() => props.setShow(false)}>
              <ModalHeader closeButton>
                <ModalTitle>"Edit {field}"</ModalTitle>
              </ModalHeader>
              <ModalBody>
               <Form>
                <Form.Group className="mb-3" controlId="exampleForm.ControlTextarea1">
                  <Form.Label>{field}</Form.Label>
                  <Form.Control as="textarea" rows={1} placeholder={field} value={props.field} onChange={handleChange}/>
                </Form.Group>
               </Form>
              </ModalBody>
              <ModalFooter>
                <Button
                  color="primary"
                  onClick = {handleSubmit} 
                >
                  Save
                </Button>
              </ModalFooter>
            </Modal>
    );
}


export default function Home(){
    const AuthContext = AuthConsumer();
    //states for the modal for editing
    const [field, setField] = useState("");
    const [show, setShow] = useState(false);
    return(
        <div className="HomePage">
            <Nav />
            <Container className="pt-2 pr-5 mt-5 mr-5">
                <Row className="pt-1">
                    <Col>User ID: </Col>
                    <Col>uid</Col>
                    <Col><Button variant="success" onClick={() =>{
                        setField("User ID");
                        setShow(true);
                    }}>Edit</Button></Col>
                </Row>
                <Row className="pt-1">
                    <Col>Password: </Col>
                    <Col>********</Col>
                    <Col><Button variant="success"onClick={() =>{
                        setField("Password");
                        setShow(true);
                    }}>Edit</Button></Col>
                </Row>
                <Row className="pt-1">
                    <Col>First Name: </Col>
                    <Col>X</Col>
                    <Col><Button variant="success"onClick={() =>{
                        setField("First Name");
                        setShow(true);
                    }}>Edit</Button></Col>
                </Row>
                <Row className="pt-1">
                    <Col>Last Name: </Col>
                    <Col>Y</Col>
                    <Col><Button variant="success"onClick={() =>{
                        setField("Last Name");
                        setShow(true);
                    }}>Edit</Button></Col>
                </Row>
                <Row className="pt-1">
                    <Col>Email: </Col>
                    <Col>email@example.com</Col>
                    <Col><Button variant="success"onClick={() =>{
                        setField("Email");
                        setShow(true);
                    }}>Edit</Button></Col>
                </Row>
            </Container>
            <Container className="pt-1 pr-5 m-5 d-flex justify-content-end">
                <Button variant="primary">Request New Certificate</Button>
            </Container>
            <EditModal field={field} setField={setField} show={show} setShow={setShow}/>
        </div>
    );
}