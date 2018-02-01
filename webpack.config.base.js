const path = require('path');

module.exports = {
  entry: ["babel-polyfill", "./react-app/app.js"],
  output: {
    path: path.join(__dirname, 'CouncilTag', 'static'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        loader: 'babel-loader',
        test: /\.js$|\.jsx$/,
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
        ]
      },
      {
        test: /\.scss$/,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader',
        ]
      },
    ],
    loaders: []
  },
  resolve: {
    modules:["node_modules", "react-app"],
    extensions: ['.js', '.jsx']
  },
  plugins: []
};
