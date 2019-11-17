import React, { useState, useEffect } from 'react';
import { useFetch } from 'react-async';
import { CircularProgress, Paper, Typography, Button, ButtonGroup } from '@material-ui/core';

function DoseEventDisplay(props) {
    return (
        <div>
            <div>Last Dose</div>
            <div>5mL/Day</div>
        </div>
    );
}

function ManualDoseSwitch(props) {
    const ml_per_second = 1.666
    const postDoseEvent = (duration) => { 
        return function() {
        console.log("Dose: ", duration);
        fetch(`/api/${props.name}/manual`, {
            method: 'POST',
            headers: {Accept: 'application/json'},
            body: JSON.stringify({time: "00:00:00", 'duration': duration})
        });
        }
    }
    return (
        <ButtonGroup size='small'>
            <Button onClick={postDoseEvent(1/ml_per_second)}>1mL</Button>
            <Button onClick={postDoseEvent(5/ml_per_second)}>5mL</Button>
            <Button onClick={postDoseEvent(10/ml_per_second)}>10mL</Button>
        </ButtonGroup>
    )
}

function DosingPump(props) {
    const API_URL = `/api/${props.name}/card`
    const {data, isLoading} = useFetch(API_URL, {headers: {Accept: "application/json"}});
    const schedule = data && data.schedule;

    return (
        <Paper>
            <Typography variant="h3">{props.name}</Typography>
            { isLoading ? <CircularProgress/> : <DoseEventDisplay schedule={schedule}/> }
            <ManualDoseSwitch name={props.name}/>
            <Typography variant="caption">Dosing Pump</Typography>
        </Paper>
    );
}


export default DosingPump;