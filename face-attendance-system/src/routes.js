import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import Capture from './pages/Capture';
import Attendance from './pages/Attendance';

const Routes = () => {
    return (
        <Router>
            <Switch>
                <Route exact path="/" component={Home} />
                <Route path="/capture" component={Capture} />
                <Route path="/attendance" component={Attendance} />
            </Switch>
        </Router>
    );
};

export default Routes;
