import { Avatar, Box, Typography, useTheme } from "@mui/material";
import { MessageProps, Variant } from ".";
import ChatbotIcon from "../../assets/chatbot_icon.png";

export const Message = ({variant, isFollowup, content}: MessageProps) => {
    const theme = useTheme();

    return (
        <Box sx={{
            display: "flex",
            flexDirection: variant === Variant.USER ? "row-reverse" : "row",
            alignItems: "flex-start",
            justifyContent: "flex-start",
            gap: theme.spacing(1),
            marginTop: isFollowup ? theme.spacing(0.5) : theme.spacing(2)
        }}>
            {!isFollowup && <Avatar 
                src={variant === Variant.USER ? "" : ChatbotIcon} 
                alt={variant === Variant.USER ? "User" : "Bot"}
                sx={{ width: 38, height: 38 }}
            />}
            <Box sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                justifyContent: "center",
                padding: theme.spacing(1),
                borderRadius: theme.spacing(1),
                backgroundColor: variant === Variant.USER ? theme.palette.primary.main : theme.palette.secondary.main,
                color: theme.palette.common.white,
                minHeight: "24px",
                ...(isFollowup && {
                    ...(variant === Variant.USER && {marginRight: "46px"}),
                    ...(variant === Variant.BOT && {marginLeft: "46px"})
                })
            }}>
                <Typography 
                    variant="body2" 
                    fontSize={12} 
                    sx={{ 
                        fontWeight: 600, 
                        "::selection": {
                            color: variant === Variant.USER ? 
                                theme.palette.secondary.main 
                            : 
                                theme.palette.primary.main
                        } 
                    }}> 
                        {content.split("\n").map((line, index) => (
                            <span key={index}>
                                {line}
                                <br />
                            </span>
                        ))}
                    </Typography>
            </Box>
        </Box>
    )
}