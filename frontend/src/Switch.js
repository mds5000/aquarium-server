import React, { useState } from 'react';
import { useFetch } from 'react-async';
import { CircularProgress, Paper, Typography, Switch as UiSwitch } from '@material-ui/core';


function ToggleSwitch(props) {
    const API_URL = `/api/${props.name}/state`
    const [state, setState] = useState(props.initialState);

    const handleChange = (event) => {
        fetch(API_URL, {
            method: "POST",
            headers: {Accept: "application/json"},
            body: JSON.stringify({state: !state})
        })
        .then(res => res.json())
        .then(data => {
            setState(data.state);
        })
        .catch(err => {
            console.log(err);
        });
    }

    return <UiSwitch checked={state} onChange={handleChange} />
}

function Switch(props) {
    const API_URL = `/api/${props.name}/card`
    const {data, isLoading} = useFetch(API_URL, {headers: {Accept: "application/json"}});
    const initialState = data && data.state;

    return (
        <Paper>
            <Typography variant="h2">{props.name}</Typography>
            { isLoading ? <CircularProgress /> : <ToggleSwitch name={props.name} initialState={initialState} /> }
        </Paper>
    )
}

export default Switch;