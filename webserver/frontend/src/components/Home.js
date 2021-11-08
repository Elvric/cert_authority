import { useNavigate } from 'react-router-dom';
import AuthConsumer from './useAuth';
import React, { useState, useEffect} from 'react';
//BootStrap react imports
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Nav from "./Nav";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function Home(){
    const AuthContext = AuthConsumer();

    return(
        <div className="HomePage">
            <Nav />
            <Container>
                <Row>
                    <Col>First Name: </Col>
                    <Col>X</Col>
                </Row>
                <Row>
                    <Col>Last Name: </Col>
                    <Col>Y</Col>
                </Row>
                <Row>
                    <Col>Email: </Col>
                    <Col>email@example.com</Col>
                </Row>
            </Container>
            <Button variant="primary">Request New Certificate</Button>
        </div>
    );
}