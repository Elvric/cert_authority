import { useNavigate } from "react-router-dom";
import AuthConsumer from "./useAuth";
import React, { useState, useEffect } from "react";

//BootStrap react imports
import Container from "react-bootstrap/Container";

import Nav from "./Nav";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import "bootstrap/dist/css/bootstrap.min.css";

const axios = require("axios").default;


export default function Home() {
    const AuthContext = AuthConsumer();
    const {isadmin} = !AuthContext.isAdmin;
    //const isadmin = true;
    const [CAState, setCAState] = useState({serial: 0, issued: 0, revoked: 0});
    console.log(CAState);
    useEffect(async function() {
        try{
            const res = await axios.get("/api/admin");
            if (res.status == 200){
                    setCAState({serial: res.data.serial, issued: res.data.issued, revoked: res.data.revoked});
                };
            }
        catch(err){
            window.alert("Error!");
        }
    }, []);
    if (!isadmin){
        return(<div> 403 Unauthorized</div>);
    }
    else{
        return(
        <div>
            <Nav />
                <Container className="pt-2 pr-5 mt-5 mr-5">
                    <Row className="pt-1">
                        <Col>Serial: </Col>
                        <Col>{CAState.serial}</Col>
                    </Row>
                    <Row className="pt-1">
                        <Col>Issued: </Col>
                        <Col>{CAState.issued}</Col>
                    </Row>
                    <Row className="pt-1">
                        <Col>Revoked: </Col>
                        <Col>{CAState.revoked}</Col>
                    </Row>
            </Container>
    </div>
    );
    }
}