import { Box, Typography, IconButton, useTheme, Card } from "@mui/material";
import { TopBarProps } from ".";
import CloseIcon from "@mui/icons-material/Close";

// Composant TopBar
const TopBar = ({ onClose }: TopBarProps) => {
  const theme = useTheme();
  return (
    <Card
      sx={{
        display: "flex",
        flexDirection: "row",
        width: "100%",
        height: "36px",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        backgroundColor: theme.palette.primary.main,
        borderRadius: 0,
        boxShadow: theme.shadows[3],
      }}
    >
      <Typography
        variant="h6"
        fontWeight={600}
        color={theme.palette.common.white}
        sx={{ userSelect: "none" }}
      >
        ChatbotS
      </Typography>
      <Box
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          fontSize: 0,
          height: "36px",
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          paddingLeft: theme.spacing(1),
        }}
      >
        <IconButton
          sx={{
            height: "20px",
            width: "20px",
            position: "relative",
          }}
          onClick={onClose}
        >
          <CloseIcon
            sx={{
              height: "20px",
              width: "20px",
              color: theme.palette.common.white,
            }}
          />
        </IconButton>
      </Box>
    </Card>
  );
};

export default TopBar;
