import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  testList: [],
  currentTestId: null,
};

const testSlice = createSlice({
  name: "testList",
  initialState,
  reducers: {
    addTest: (state, action) => {
      state.testList.push(action.payload);
    },
    removeTest: (state, action) => {
      state.testList = state.testList.filter((test) => test.id !== action.payload);
    },
    setCurrentTestId: (state, action) => {
      state.currentTestId = action.payload;
    },
    setName: (state, action) => {
      state.testList[state.currentTestId - 1].name = action.payload;
    },
    setData: (state, action) => {
      state.testList[state.currentTestId - 1].data = [action.payload];
    },
  },
});

export const { addTest, removeTest, setCurrentTestId, setName, setData } = testSlice.actions;
export default testSlice.reducer;
