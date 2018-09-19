import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';


const styles = {
  root: {
    height: 120
  },
  temp: {
    display: "flex",
    justifyContent: "center",
    fontFamily: "roboto",
    fontSize: 60
  }

};

class Temperature extends React.Component {
  state = {
    value: -1,
  };

  handleChange = (event, value) => {
    this.setState({ value });
  };

  componentDidMount() {
      fetch("api/temperature")
      .then( res => {
          return res.json();
      }).then( data => {
          this.setState({ value: data.value });
          console.log(data);
      }).catch( () => {
          console.log("ERROR Getting Temperature");
      });
  }

  render() {
    const { classes } = this.props;
    const { value } = this.state;

    var disp = (
        <div className={classes.temp}>
          {value}
          <span style={{fontSize: 20, position: "relative", bottom: -20}}>&deg;F</span>
        </div>
    );
    if (value < 0) {
        disp = <CircularProgress/>
    }

    return (
        <Paper className={classes.root}>
          {disp}
          <Typography variant="caption" align="center">Temperature</Typography>
        </Paper>
    );
  }
}

export default withStyles(styles)(Temperature);