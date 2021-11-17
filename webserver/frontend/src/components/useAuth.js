"use strict;";
import * as React from "react";
const axios = require("axios").default;
const https = require("https");

const authContext = React.createContext();
const parseJwt = (token) => {
  try {
    let jwt = Buffer.from(token.split('.')[1], 'base64').toString();
    console.log(jwt)
    return JSON.parse(jwt);
  } catch (e) {
    return null;
  }
};

function useAuth() {
  /*
    authed: is the user authed or not
    isLoading: tell components if the check of the token is done or not
  */
  const [state, setState] = React.useState({
    authed: false,
    isLoading: true,
    isAdmin:false,
  });

  return {
    state,
    setToken: (token) => {
      if (token !== null) {
        const decoded = parseJwt(token);
        console.log(decoded["admin"]);
        setState({ authed: true, isLoading: false, isAdmin: decoded["admin"]});
        axios.defaults.headers.common["x-access-tokens"] = token;
      }
    },
    login: async (uid, password) => {
      // const instance = axios.create({
      //   httpsAgent: new https.Agent({
      //     ca: [fs.readFileSync("server-cert.pem")], //root CA cert
      //   }),
      //   baseURL: "https://webserver.imovies/api/login",
      // });
      try {
        const res = await axios.post("/api/login", {
          uid,
          password,
        });
        if (res.status === 200) {
          const token = res.data.token;
          const decoded = parseJwt(token);
          const isadmin = decoded["admin"]
          axios.defaults.headers.common["x-access-tokens"] = token;
          window.localStorage.setItem("token", token);
          return new Promise((res) => {
            setState({ authed: true, isLoading: false, isAdmin: (isadmin === 1) });
            res();
        });
      }
      } catch (err) {
        window.alert("Invalid credentials");
        setState((s) => ({ ...s, isLoading: false }));
      }
    },
    loginWithCert: async (cert) => {
      // const instance = axios.create({
      //   httpsAgent: new https.Agent({
      //     ca: [ fs.readFileSync('server-cert.pem') ], //root CA cert
      //     key: fs.readFileSync('client-key.pem'),
      //     cert: cert,
      //   }),
      //   baseURL : 'https://webserver.imovies/api/login_with_cert'
      // });
      try {
          const res = await axios.post("/api/login_with_cert", {
            cert
        });

        if (res.status === 200) {
          const token = res.data.token;
          const decoded = parseJwt(token);
          const isadmin = decoded["admin"];
          axios.defaults.headers.common["x-access-tokens"] = token;
          window.localStorage.setItem("token", token);
          return new Promise((res) => {
            setState({ authed: true, isLoading: false, isAdmin: (isadmin === 1) });
            res();
        });
      }
      } catch (err) {
        window.alert("Invalid credentials");
        setState((s) => ({ ...s, isLoading: false }));
      }
    },
    logout: () => {
      localStorage.removeItem("token");
      return new Promise((res) => {
        setState((s) => ({ authed: false, isLoading: false, isAdmin: false }));
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

  // Fetch the token from local storage if it exsits
  React.useEffect(() => {
    (async () => {
      const token = await localStorage.getItem("token");
      auth.setToken(token);
    })();
  }, []);

  return <authContext.Provider value={auth}>{children}</authContext.Provider>;
}

export default function AuthConsumer() {
  //The AuthConsumer must be enclosed with a AuthProvider
  return React.useContext(authContext);
}
