import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addTest, removeTest, setCurrentTestId } from "../store/testSlice";
import TrashImg from "/images/trash.svg";
import { setIsAuthenticated } from "../store/profileSlice";

function ListPage() {
  
  const navigate = useNavigate();
  const testList = useSelector((state) => state.testList.testList);
  const dispatch = useDispatch();
  const isAuthenticated = useSelector((state) => state.profile.isAuthenticated);

  const createTest = () => {
    dispatch(
      addTest({
        id: testList.length + 1,
        name: "Тест " + (testList.length + 1),
        data: [],
      })
    );
    dispatch(setCurrentTestId(testList.length + 1));
    navigate("/");
  };

  const exit = () => {
    dispatch(setIsAuthenticated(false));
    navigate("/auth");
  };

  const deleteTest = (id) => {
    dispatch(removeTest(id));
    dispatch(setCurrentTestId(null));
  }

  if (!isAuthenticated) { 
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="w-[47.8125rem] h-[54.125rem] bg-white rounded-[28px] flex flex-col items-center
        justify-between gap-8 relative border-3 border-black px-14 pt-22 pb-14">
          <p className="text-black text-2xl">Вы не авторизованы</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div
        className="w-[47.8125rem] h-[54.125rem] bg-white rounded-[28px] flex flex-col items-center
      justify-between gap-8 relative border-3 border-black px-14 pt-22 pb-14"
      >
        <div
          id="header-container"
          className="w-full h-[3.9375rem] flex items-center justify-between"
        >
          <p className="text-black text-2xl">Ваши тесты: {testList.length}</p>
          <div
            id="create-container"
            className="h-full flex items-center justify-center gap-4"
          >
            <button
              onClick={createTest}
              className="w-[11.875rem] h-full bg-white rounded-[18px] text-black text-2xl border-3 border-black cursor-pointer hover:scale-105 transition-[scale] duration-300 ease-in-out"
            >
              Создать +
            </button>
          </div>
        </div>
        <div
          id="tests-container"
          className="w-full h-full flex flex-col items-center justify-start gap-3 px-4 py-6 border-3 border-black rounded-[28px] overflow-y-auto"
        >
          {testList.map((test) => (
            <div
              key={test.id}
              className="w-full h-[5.625rem] gap-4 flex items-center justify-between"
            >
              <div
                id="see-test-block"
                className="w-full h-full flex items-center justify-between p-6 border-3 border-black rounded-[20px]"
              >
                <p className="text-black text-xl">
                  {test.id}. {test.name}
                </p>
                <p
                  onClick={() => navigate(`/testInfo/${test.id}`)}
                  className="text-black text-xl cursor-pointer hover:scale-105 transition-[scale] duration-300 ease-in-out"
                >
                  Посмотреть -&gt;
                </p>
              </div>
              <div
                id="delete-test-block"
                onClick={() => deleteTest(test.id)}
                className="h-full aspect-square flex items-center justify-center bg-white rounded-[18px] text-black text-2xl border-3 border-black cursor-pointer hover:scale-105 transition-[scale] duration-300 ease-in-out"
              >
                <img
                  src={TrashImg}
                  alt="trash"
                  className="w-[1.5625rem] aspect-square"
                />
              </div>
            </div>
          ))}
        </div>
        <p
          id="exit"
          onClick={exit}
          className="text-black text-xl absolute top-6 right-13 border-b-2 border-black cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        >
          Выйти из аккаунта
        </p>
      </div>
    </div>
  );
}

export default ListPage;
