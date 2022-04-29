// Require and initialize outside of your main handler
const mysql = require('serverless-mysql')({
    config: {
      host     : "HerediVar_ahdoebm1",
      database : "SRV011.img.med.uni-tuebingen.de",
      user     : "ahdoebm1",
      password : "20220303"
    }
  })
  
  // Main handler function
  exports.handler = async (event, context) => {
    // Run your query
    let results = await mysql.query('SELECT * FROM table')
  
    // Run clean up function
    await mysql.end()
  
    // Return the results
    return results
  }

await mysql.connect()

let results = await query('SELECT * FROM variant WHERE id=15')
console.log(results)