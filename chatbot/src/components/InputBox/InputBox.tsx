import { useState } from "react";
import { TextField, Box, useTheme, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { InputBoxProps } from "./types";

export const InputBox = ({ onSubmit, loading }: InputBoxProps) => {
  const theme = useTheme();
  const [userQuestion, setUserQuestion] = useState<string>("");

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        gap: theme.spacing(1),
        padding: theme.spacing(1),
      }}
    >
      <TextField
        id="testField"
        label="Write here your question"
        fullWidth
        multiline
        size="small"
        maxRows={4}
        variant="outlined"
        onChange={(event: React.ChangeEvent<HTMLInputElement>): void => {
          !loading && setUserQuestion(event?.currentTarget.value);
        }}
        value={userQuestion}
        InputProps={{
          sx: {
            borderRadius: theme.spacing(2),
            backgroundColor: theme.palette.action.disabledBackground,
            fontWeight: 600,
            color: theme.palette.common.black,
            fontSize: 14,
          },
          onKeyPress: (e) => {
            if (loading) {
                e.preventDefault();
                return;
            };
            if (e.key === "Enter" && !(e.shiftKey || e.ctrlKey)) {
              e.preventDefault();
              onSubmit(userQuestion);
              setUserQuestion("");
            }
          },
        }}
        InputLabelProps={{
          sx: {
            fontWeight: 600,
            color: theme.palette.common.black,
            borderColor: "transparent",
            fontSize: 14,
          },
        }}
      ></TextField>
      <IconButton
        sx={{ width: 32, height: 32 }}
        onClick={() => {
          onSubmit(userQuestion);
          setUserQuestion("");
        }}
      >
        <SendIcon
          sx={{ color: theme.palette.primary.main, width: 28, height: 28 }}
        />
      </IconButton>
    </Box>
  );
};
