import {
  Outlet,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";
import NextImg from "/images/next.svg";
import FirstTask from "./FirstTask";
import SecondTask from "./SecondTask";

function TasksPage() {
  const isFirstTask = useParams().isFirstTask;
  const navigate = useNavigate();

  return (
    <>
      <Routes>
        <Route
          path="/"
          element={
            <div className="w-full h-full">
              <div className="w-[59.75rem] h-full bg-black/[5%] outline-[3px] outline-black absolute top-0 left-1/2 -translate-x-1/2 z-0 px-12 flex flex-col items-center justify-center gap-[1.875rem]">
                <div className="w-full text-center justify-center text-black text-6xl font-semibold z-10">
                  {isFirstTask === "true"
                    ? "Форма для регистрации"
                    : isFirstTask === "false" ? "Захват внимания" : ""}
                </div>
                <div className="w-full text-center justify-center text-black/80 text-2xl z-10">
                  {isFirstTask === "true" ? (
                    <p>
                      Давайте представим, что вы хотите зарегистрироваться на
                      некотором сайте. В серой зоне Вам необходимо расположить
                      кнопку регистрации среди остальных типичных элементов
                      формы регистрации. На следующей странице прочитайте
                      задание, подумайте, куда бы хотели расположить элемент, а
                      затем нажмите кнопку "Начать". После нажатия кнопки
                      смотрите в нужную Вам точку в течение 5 секунд. Учитывайте, что
                      в располагаемой точке будет находиться середина элемента
                    </p>
                  ) : isFirstTask === "false" ? (
                    <p>
                      Сейчас перед Вами на несколько секунд будут появляться
                      различные рекламные баннеры. От Вас не требуется каких-то
                      специфических действий. После этого задания мы покажем,
                      насколько сильно рекламные баннеры захватили Ваше внимание
                      (с помощью саккад)
                    </p>
                  ) : ""}
                </div>

                <div className="flex gap-4 z-10">
                  <img
                    src={NextImg}
                    alt="previous"
                    onClick={() => navigate("/calibration")}
                    className={`w-24 h-24 rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out
                      ${isFirstTask === "true" ? "flex" : "hidden"}`}
                  />
                  <img
                    src={NextImg}
                    alt="next"
                    onClick={() =>
                      navigate(
                        `/tasks/${isFirstTask}/${isFirstTask === "true" ? "task1" : "task2"}`
                      )
                    }
                    className="w-24 h-24 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
                  />
                </div>
              </div>
            </div>
          }
        />
        <Route path="task1" element={<FirstTask />} />
        <Route path="task2" element={<SecondTask />} />
      </Routes>
      <Outlet />
    </>
  );
}

export default TasksPage;
