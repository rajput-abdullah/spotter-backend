import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import TripForm from './components/TripForm';
import RouteInstructions from './components/RouteInstructions';

const App: React.FC = () => {
  return (
    <Router>
      <div>
        <h1>ELD Route Planner</h1>
        <Switch>
          <Route path="/" exact component={TripForm} />
          <Route path="/instructions" component={RouteInstructions} />
        </Switch>
      </div>
    </Router>
  );
};

export default App;