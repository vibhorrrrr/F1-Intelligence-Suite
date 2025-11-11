const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  // Start the Dash app
  const pythonProcess = spawn('python', [
    path.join(process.cwd(), 'ui/landing_page.py'),
    '--port', '8888'
  ]);

  // Log output for debugging
  pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  // Return a response
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'F1 Strategy Suite is running' }),
  };
};
