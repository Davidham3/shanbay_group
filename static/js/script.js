// Event handling
document.addEventListener("DOMContentLoaded",
  function (event) {
    (  function (window) {
      pattern = window.location['pathname'].split('/').pop()
      if (pattern !== "" && pattern !== null) {
        element = document.getElementById(pattern);
        if (element !== null)
          document.getElementById(pattern).className += ' myactive';
      }
    })(window);
  }
);

document.addEventListener("DOMContentLoaded",
  function (event) {
    document.getElementById('kick_out').addEventListener("click", 
      function () {
        //window.open("http://www.jb51.net");
        $ajaxUtils.sendGetRequest('/kick_out', 
          function (request) {
            var text = JSON.parse(request.responseText);
            for(var i=0; i<text['data'].length; i++)
              window.open('https://www.shanbay.com/team/manage/?page='+text['data'][i]+'#p1');
          }
        )
      }
    )
  } 
);


document.addEventListener("DOMContentLoaded",
  function (event) {
    // Unobtrusive event binding
    document.getElementById('refresh')
      .addEventListener("click", function () {
        $ajaxUtils
          .sendGetRequest("/data/check_maxpage", 
            function (request) {
              document.getElementById("tbody").innerHTML = '';
              var maxpage = request.responseText;
              document.getElementById('content').innerHTML = '当前进度: 0.00%';
              for (var i=1; i<parseInt(maxpage)+1; i++) {
                $ajaxUtils.sendGetRequest("/data/"+i,
                  function (request2) {
                    var content = JSON.parse(request2.responseText);
                    (function (content) {
                      document.getElementById("tbody").innerHTML += content['content'];
                      document.getElementById('content').innerHTML = '当前进度: '+Math.round(100.0*(parseInt(content['page']))/(parseInt(maxpage)))+'%';
                      if (content['page'] == maxpage) {
                        window.location.href = window.location['pathname'];
                      }
                    })(content);
                  });
              }
            });
      });
  }
);

function getData(page) {
  var xhr = getRequestObject();
  xhr.open("GET", "data/"+page, true);
  xhr.onreadystatechange = function(){
    var XMLHttpReq = xhr;
    if ((XMLHttpReq.readyState == 4) && (XMLHttpReq.status == 200)) {
      return XMLHttpReq.responseText;
    };
  };
  xhr.send();
}


function getRequestObject() {
  if (XMLHttpRequest) {
    return (new XMLHttpRequest());
  } 
  else if (ActiveXObject) {
    // For very old IE browsers (optional)
    return (new ActiveXObject("Microsoft.XMLHTTP"));
  } 
  else {
    global.alert("Ajax is not supported!");
    return(null); 
  }
}
