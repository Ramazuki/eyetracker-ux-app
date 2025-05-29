import { configureStore } from "@reduxjs/toolkit";
import testReducer from "./testSlice";
import profileReducer from "./profileSlice";

const store = configureStore({
  reducer: {
    testList: testReducer,
    profile: profileReducer,
  },
});

export default store;