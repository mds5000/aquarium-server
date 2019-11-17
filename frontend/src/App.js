import React from 'react';
import { useFetch } from 'react-async';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import CssBaseline from '@material-ui/core/CssBaseline';

import BottomBar from './BottomBar';
import Temperature from './Temperature';
import Switch from './Switch';
import DosingPump from './DosingPump';
import { Grid } from '@material-ui/core';


function App(props) {
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
  const SERVICES_URL = "/api/services"
  const {data, isLoading} = useFetch(SERVICES_URL, {headers: {Accept: "application/json"}});

  if (isLoading) {
    return <div> Still loading... </div>;
  }

  const services = data && data.services;
  const cards = services.map((props) => {
    switch (props.type) {
    case "AnalogSensor":
      return <Grid item key={props.name}><Temperature {...props} /></Grid>;
    case "Switch": 
      return <Grid item key={props.name}><Switch {...props} /></Grid>;
    case "DosingPump":
      return <Grid item key={props.name}><DosingPump {...props} /></Grid>;
    case "KessilController":
    default:
      console.log(`Unknown service of type '${props.type}'`);
      return;
    }
  });
  const card_items = cards.filter(x => x ? true : false);

  return (
    <Grid container direction='column' spacing='2'>
      {card_items}
    </Grid>
  )
};

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
