module.exports = {
    entry: "./react-app/App.jsx",
    output: {
        path: "./CouncilTag/static",
        filename: "bundle.js"
    },
    resolve:{
        modules:[
            "./node_modules", 
            "./react-app"
        ],
        extensions:["js", "jsx", "css", "scsss"]
    },
    devServer:{
        contenPath: "./CouncilTag/static",
        port:5000
    }
}