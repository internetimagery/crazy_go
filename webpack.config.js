module.exports = {
    resolve: {
      modules: ['build/node_modules']
    },
    module: {
	    rules: [
	      {
		test: /\.css$/,
		use: [
		  'style-loader',
		  'css-loader',
		]
	      },
	      {
		test: /\.py$/,
		loader: "py-loader",
		options: {
		  compiler: 'pj'
		}
	      }
	    ]
    }
};
