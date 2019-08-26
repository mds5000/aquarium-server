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
    const postDoseEvent = () => {
        fetch(`/api/${props.name}/manual`, {
            method: 'POST',
            headers: {Accept: 'application/json'},
            body: JSON.stringify({time: "00:00:00", duration: 5})
        });
    }
    return (
        <ButtonGroup size='small'>
            <Button onClick={postDoseEvent}>1mL</Button>
            <Button>5mL</Button>
            <Button>10mL</Button>
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