import React, { useEffect, useState } from 'react';
import useFetch from 'react-fetch-hook';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

import BottomBar from './BottomBar';
import Temperature from './Temperature';


function App(props) {
  const { classes } = props;
  return (
    <Router>
      <CssBaseline />
      <Route exact path="/" component={ServicesList} />
      <Route path="/settings" component={Settings} />
      <Route path="/charts" component={Charts} />
      <BottomBar/>
    </Router>
  )
};

function ServicesList() {
  const SERVICES_API = "/api/services"
  const fetch = useFetch(SERVICES_API);

  if (fetch.isLoading) {
    return <div> Still loading... </div>;
  }

  const services = fetch.data && fetch.data.services || [];

  const cards = services.map((props) => {
    switch (props.type) {
    case "AnalogSensor":
      return <Temperature key={props.name} {...props} />;
    case "Switch": 
      return <Switch key={props.name} {...props} />;
    case "DosingPump":
    case "KessilController":
    default:
      console.log(`Unknown service of type '${props.type}'`);
      return;
    }
  });
  const card_items = cards.filter(x => x ? true : false);

  return (
    <div>
      {card_items}
    </div>
  )
};

function Switch(props) {
  return <div>Switch</div>
}

function Settings(props) {
  return (
    <div> Settings </div>
  )
};
function Charts(props) {
  return (
    <div> Charts </div>
  )
};


export default App;
