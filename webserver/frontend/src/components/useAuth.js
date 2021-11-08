import * as React from "react";

const authContext = React.createContext();

function useAuth() {
  const [authed, setAuthed] = React.useState(false);

  return {
    authed,
    login() {
        //TO DO: setup fetch from api
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
    }
  };
}

export function AuthProvider({ children }) {
    /*
        Takes components children as argument
        Children can subscribe to the context that is passed as value props from Provider
        In this case is the context
    */
    const auth = useAuth();

    return (
        <authContext.Provider value={auth}>
          {children}
        </authContext.Provider>
    );
}

export default function AuthConsumer() {
    //The AuthConsumer must be enclosed with a AuthProvider
    return React.useContext(authContext);
}