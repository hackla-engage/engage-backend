var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var config = require('./webpack.config.base.js')
console.log(config);
config.devtool = "#eval-source-map"


var ip = 'localhost';
config.entry = [
    'webpack-dev-server/client?http://' + ip + ':3000',
    'webpack/hot/only-dev-server',
    './react-app/app.js',
  ]


config.output.publicPath = 'http://' + ip + ":3000" + "/assests/bundles/";

config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(),
  new BundleTracker({filename: './webpack-stats-local.json'}),
])

config.module.loaders.push(
  { test: /\.jsx?$/, exclude: /node_modules/, loaders: ['react-hot', 'babel'] }
)

module.exports = config