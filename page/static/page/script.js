function weightedMean(arrValues, arrWeights) {

  var result = arrValues.map(function (value, i) {

    var weight = arrWeights[i];
    var sum = value * weight;

    return [sum, weight];
  }).reduce(function (p, c) {

    return [p[0] + c[0], p[1] + c[1]];
  }, [0, 0]);

  return result[0] / result[1];
}

function calcMean(){
    $(".predmet-radek").each(function(i, obj){
        var znamky = [];
        var vahy = [];
        $(obj).find(".znamka-v").each(function(y, zn){
            var znam = $(zn).find(".znamka").text();
            znam = +znam.replace("-", ".5");
            var vah = +$(zn).find(".vaha").text();
            if(!isNaN(znam) && !isNaN(vah) && znam >= 1 && znam <= 5 && vah >= 1 && vah <= 10){
                znamky.push(znam);
                vahy.push(vah);
                $(zn).removeClass("inactive");
            }
            else{
                $(zn).addClass("inactive");
            }

        });
        $(obj).find(".prumer").text(weightedMean(znamky, vahy).toFixed(2));
    });

}

function addZnamka(obj){
    obj.before("<div class=\"znamka-v added inactive tooltip\"><div class=\"znamka\" contentEditable=\"true\"></div><div class=\"vaha\" contentEditable=\"true\"></div></div>");
    obj.prev().on("input", calcMean);
}

function load(pololeti){
    var polstring = "index.html";
    if (pololeti == "1" || pololeti == "2") polstring += "?pololeti=" + pololeti;
    $.get(polstring, function(data) {
        $("body").html(data);
        main();
      })
    .fail(function() {
    $("body").html("<p>Error</p>");
    });
}

function main(){
    calcMean();
    $(".znamka, .vaha").on("input", calcMean);
}