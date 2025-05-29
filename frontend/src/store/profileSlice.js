import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    login: "admin",
    password: "admin",
    isAuthenticated: false,
}

const profileSlice = createSlice({
    name: "profile",
    initialState,
    reducers: {
        setIsAuthenticated: (state, action) => {
            state.isAuthenticated = action.payload;
        },
    },
});

export const { setIsAuthenticated } = profileSlice.actions;
export default profileSlice.reducer;