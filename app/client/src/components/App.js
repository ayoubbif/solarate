import React, { Component } from 'react';
import UtilityRateFinder from './UtilityRateFinder';

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <>
                <UtilityRateFinder/>
            </>
        );
    }
}
