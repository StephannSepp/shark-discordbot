
import io

from disnake import CmdInter
from disnake import File
from disnake.ext import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class TabletTexter(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="tablet-text", description="Amesame平板顯示訊息，雙空格代替換行")
    async def tablet_text(self, inter: CmdInter, text: str):

        await inter.response.defer()
        text = text.replace("  ", "\n")

        # def find_coefs(original_coords, warped_coords):
        #     matrix = []
        #     for p1, p2 in zip(original_coords, warped_coords):
        #         matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        #         matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
        #
        #     A = np.matrix(matrix, dtype=float)
        #     B = np.array(warped_coords).reshape(8)
        #
        #     res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
        #     return np.array(res).reshape(8)

        base_image = Image.open("static/base.png")
        text_image = Image.new('RGBA', (960, 480))
        text_draw = ImageDraw.Draw(text_image)
        W, H = text_image.size

        # Responsive font size
        fontsize = 24
        font = ImageFont.truetype("static/NotoSansTC-Thin.woff", fontsize)
        while (
            font.getsize(text)[0] < text_image.size[0]
            and font.getsize(text)[1] < text_image.size[1]
        ):
            fontsize += 1
            font = ImageFont.truetype("static/NotoSansTC-Thin.woff", fontsize)

        # Draw text
        w, h = text_draw.textsize(text, font=font)
        text_draw.text(
            xy=((W-w)/2, (H-h)/2), text=text, fill=(0, 0, 0, 255), font=font, align="center"
        )
        # coefs = find_coefs(
        #     [(0, 0), (W, 0), (W, H), (0, H)],
        #     [(-120, 20), (W-5, -100), (W+70, H-210), (-30, H-110)]
        # )
        coefs = [
            1.07076140e+00, 1.86397611e-01, -1.20000000e+02, -1.19865941e-01,
            7.42762801e-01, 2.00000000e+01, -5.13405888e-05, 3.67463097e-05
        ]
        text_image = text_image.transform((W*2, H*2), Image.PERSPECTIVE, data=coefs)
        text_image = text_image.resize((885, 380))
        base_image.paste(text_image, (260, 525), text_image)

        with io.BytesIO() as image_binary:
            base_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await inter.followup.send(file=File(fp=image_binary, filename='output.png'))


def setup(bot: commands.InteractionBot):
    bot.add_cog(TabletTexter(bot))
