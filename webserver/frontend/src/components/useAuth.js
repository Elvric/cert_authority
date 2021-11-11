'use strict;'
import * as React from "react";
const axios = require("axios").default;
const https = require('https');

const authContext = React.createContext();

function useAuth() {
  const [authed, setAuthed] = React.useState(false);

  return {
    authed,
    login(user, password) {
      const instance = axios.create({
        httpsAgent: new https.Agent({
          ca: [ fs.readFileSync('server-cert.pem') ], //root CA cert
        }),
        baseURL : 'https://webserver.imovies/api/login'
      });
      axios.post(
        {
          user: user,
          password: password
        });
      return new Promise((res) => {
        setAuthed(true);
        res();
      });
    },
    loginWithCert(cert) {
      const instance = axios.create({
        httpsAgent: new https.Agent({
          ca: [ fs.readFileSync('server-cert.pem') ], //root CA cert
          key: fs.readFileSync('client-key.pem'),
          cert: cert,
        }),
        baseURL : 'https://webserver.imovies/api/login_with_cert'
      });
      axios.get();
        return new Promise((res) => {
          setAuthed(true);
          res();
        });
    },
    logout() {
      return new Promise((res) => {
        setAuthed(false);
        res();
      });
    },
  };
}

export function AuthProvider({ children }) {
  /*
        Takes components children as argument
        Children can subscribe to the context that is passed as value props from Provider
        In this case is the context
    */
  const auth = useAuth();

  return <authContext.Provider value={auth}>{children}</authContext.Provider>;
}

export default function AuthConsumer() {
  //The AuthConsumer must be enclosed with a AuthProvider
  return React.useContext(authContext);
}
