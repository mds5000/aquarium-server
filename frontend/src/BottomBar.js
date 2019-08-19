import React from 'react';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import HomeIcon from '@material-ui/icons/Home';
import SettingsSharpIcon from '@material-ui/icons/SettingsSharp';
import ShowChartIcon from '@material-ui/icons/ShowChart';


const styles = {
  root: {
    width: '100%',
    position: 'absolute',
    bottom: 0
  }
};

class BottomBar extends React.Component {
  state = {
    value: 0,
  };

  handleChange = (event, value) => {
    this.setState({ value });
  };

  render() {
    const { classes } = this.props;
    const { value } = this.state;

    return (
      <BottomNavigation
        value={value}
        onChange={this.handleChange}
        showLabels
        className={classes.root}
      >
        <BottomNavigationAction label="Home" icon={<HomeIcon/>} to="/" component={Link} />
        <BottomNavigationAction label="Charts" icon={<ShowChartIcon/>} to="/charts" component={Link} />
        <BottomNavigationAction label="Settings" icon={<SettingsSharpIcon/>} to="/settings" component={Link} />
      </BottomNavigation>
    );
  }
}

export default withStyles(styles)(BottomBar);