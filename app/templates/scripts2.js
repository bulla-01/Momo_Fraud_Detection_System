// scripts.js
document.addEventListener("DOMContentLoaded", function () {
  const ctxArea = document.getElementById("areaChart").getContext("2d");
  const barChartCtx = document.getElementById("barChart").getContext("2d");
  const rangeInput = document.getElementById("chartRange");
  const rangeLabel = document.getElementById("rangeLabel");
  const chartTypeSelect = document.getElementById("chartType");

  let areaChart = new Chart(ctxArea, {
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
      datasets: [{
        label: "Suspicious Transactions",
        data: [12, 19, 3, 5, 2],
        borderColor: "#00ffff",
        backgroundColor: "rgba(0, 255, 255, 0.2)",
        fill: true
      }]
    }
  });

  let barChart = new Chart(barChartCtx, {
    type: "bar",
    data: {
      labels: ["A", "B", "C"],
      datasets: [{
        label: "Summary",
        data: [5, 10, 8],
        backgroundColor: ["#ff00ff", "#00ffff", "#ffcc00"]
      }]
    }
  });

  rangeInput.addEventListener("input", function () {
    rangeLabel.textContent = rangeInput.value;
    areaChart.data.datasets[0].data = Array(5).fill().map(() => Math.floor(Math.random() * rangeInput.value));
    areaChart.update();
  });

  chartTypeSelect.addEventListener("change", function () {
    const newType = chartTypeSelect.value;
    areaChart.destroy();
    areaChart = new Chart(ctxArea, {
      type: newType,
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        datasets: [{
          label: "Suspicious Transactions",
          data: [12, 19, 3, 5, 2],
          borderColor: "#00ffff",
          backgroundColor: "rgba(0, 255, 255, 0.2)",
          fill: true
        }]
      }
    });
  });
});
