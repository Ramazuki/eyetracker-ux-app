import { useNavigate, useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

function TestInfoPage() {

  const testList = useSelector((state) => state.testList.testList);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const testId = useParams().testId;

  const handleDownload = () => {
    const data = testList[testId - 1].data;
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const rows = data.map(row =>
      headers.map(field => {
        const value = row[field] ?? "";
        return `"${String(value).replace(/"/g, '""')}"`;
      }).join(",")
    );
    const csvContent = [headers.join(","), ...rows].join("\r\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${testList[testId - 1].name}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div
        className="w-[47.8125rem] h-[54.125rem] bg-white rounded-[28px] flex flex-col items-center
    justify-start gap-8 relative border-3 border-black px-24 pt-22"
      >
        <h1 className="text-black text-5xl">Информация о тесте</h1>
        <div id="test-info-container" className="w-full h-[11rem] border-3 border-black rounded-[28px] p-8 flex flex-col items-start justify-center gap-7">
          <p id="test-name" className="text-black text-3xl">Название: {testList[testId - 1].name}</p>
          <p id="test-token" className="text-black text-3xl">Токен: ...</p>
        </div>
        {testList[testId - 1].data.length === 0 ? (
            <p className="w-full h-[4.1875rem] flex items-center justify-center text-black text-2xl">Нет данных</p>
        ) : (
            <button id="getData" onClick={handleDownload} className="w-full h-[4.1875rem] flex items-center justify-center bg-white rounded-[18px] text-black text-2xl border-3 border-black cursor-pointer hover:scale-105 transition-[scale] duration-300 ease-in-out">Получить данные</button>
        )}
        <p id="previousPage" onClick={() => navigate("/list")} className="text-black text-3xl absolute top-6 left-12 cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out">
          &lt;-
        </p>
      </div>
    </div>
  );
}

export default TestInfoPage;
