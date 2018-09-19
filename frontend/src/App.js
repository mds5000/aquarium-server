import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

import BottomBar from './BottomBar';
import Temperature from './Temperature';

const styles = theme => ({
  root: {
    padding: theme.spacing.unit * 2
  },
  box: {
    height: 140
  },
});

function App(props) {
  const { classes } = props;
  return (
    <React.Fragment>
      <CssBaseline />
      <Grid container spacing={16} className={classes.root}>
        <Grid item xs={6} className={classes.box}>
          <Temperature />
        </Grid>
        <Grid item xs={6} className={classes.box}>
          <Paper>Item 2</Paper>
        </Grid>
        <Grid item xs={6} className={classes.box}>
          <Paper>Item 3</Paper>
        </Grid>
        <Grid item xs={6} className={classes.box}>
          <Paper>Item 4</Paper>
        </Grid>
      </Grid>
      <BottomBar/>
    </React.Fragment>
  );
}

export default withStyles(styles)(App);
